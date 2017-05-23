

from cerbero.commands import Command, register_command
from cerbero.build.cookbook import CookBook
from cerbero.build.source import SourceType
from cerbero.packages.packagesstore import PackagesStore
from cerbero.bootstrap.build_tools import BuildTools
from cerbero.utils import _, N_, ArgparseArgument, remove_list_duplicates
from cerbero.utils import messages as m
from setuptools.sandbox import run_setup


class Bundle(Command):
    doc = N_('Bundle package ')
    name = 'bundle'

    def __init__(self, args=[]):
        args = [
            ArgparseArgument('packages', nargs='+', 
                             help=_('packages to bundle')),
            ArgparseArgument('--pkg-dir', default='.',
                             help=_('directory where the package in it')),

            ArgparseArgument('--out-dir', default='.',
                             help=_('diretory where the bundle packages to be placed')),
            
            ArgparseArgument('--gen-desc-only', default='.',
                             help=_('generate bundle desc file only'))
        ]
        Command.__init__(self, args)

    def run(self, config, args):
        packages = []
        recipes = []
        bundle_recipes = []
        bundle_dirs = []
        setup_args = ['sdist']

        if not config.uninstalled:
            m.error("Can only be run on cerbero-uninstalled")

        store = PackagesStore(config)
        cookbook = CookBook(config)

        packages = list(args.packages)

        for p in packages:
            package = store.get_package(p)
            if hasattr(package, 'list_packages'):
                packages += package.list_packages()
        packages = remove_list_duplicates(packages)

        for p in packages:
            package = store.get_package(p)
            if hasattr(package, 'deps'):
                packages += package.deps
        packages = remove_list_duplicates(packages)

        for p in packages:
            package = store.get_package(p)
            recipes += package.recipes_dependencies()
        recipes += args.add_recipe

        for r in recipes:
            bundle_recipes += cookbook.list_recipe_deps(r)
        bundle_recipes = remove_list_duplicates(bundle_recipes)

        for p in packages:
            setup_args.append('--package=' + p)

        for r in bundle_recipes:
            setup_args.append('--recipe=' + r.name)
            if r.stype != SourceType.CUSTOM:
                bundle_dirs.append(r.repo_dir)

        if not args.no_bootstrap:
            build_tools = BuildTools(config)
            bs_recipes = build_tools.BUILD_TOOLS + \
                         build_tools.PLAT_BUILD_TOOLS.get(config.platform, [])
            b_recipes = []
            for r in bs_recipes:
                b_recipes += cookbook.list_recipe_deps(r)
            b_recipes = remove_list_duplicates(b_recipes)

            for r in b_recipes:
                if r.stype != SourceType.CUSTOM:
                    bundle_dirs.append(r.repo_dir)

        setup_args.append('--source-dirs=' + ','.join(bundle_dirs))

        command = str(config._relative_path('setup.py'))
        run_setup(command, setup_args)

register_command(BundleSource)
