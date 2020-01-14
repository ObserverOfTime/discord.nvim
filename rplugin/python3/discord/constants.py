import re

_rc_ignore = r'^(\.?{0}rc(\.js(on)?|\.ya?ml)?|{0}\.config\.js|\.{0}ignore)$'

#: The ID of the Discord RPC client.
CLIENT_ID = '492721776145596416'

#: A mapping of special filetypes to filename patterns.
SPECIAL_FTS = {
    'angular': re.compile(r'\.?angular(-cli)?.json'),
    'ansible': re.compile(r'^(ansible\.cfg|site.ya?ml|hosts)$'),
    'apache': re.compile(r'^(.*(apache|httpd)\.conf|\.htaccess)$'),
    'appveyor': re.compile(r'^\.?appveyor\.ya?ml$'),
    'babel': re.compile(_rc_ignore.format('babel')),
    'bower': re.compile(r'^(\.bowerrc|bower\.json)$'),
    'browserslist': re.compile(r'^\.?browserslist(rc|)$'),
    'bundler': re.compile(r'^(Gemfile(\.lock)|\.gemspec)$'),
    'cargo': re.compile(r'^Cargo\.(toml|lock)$'),
    'circleci': re.compile(r'^circle\.yml$'),
    'codacy': re.compile(r'\.codacy\.ya?ml$'),
    'codeclimate': re.compile(r'^\.codeclimate\.(ya?ml|json)$'),
    'codecov': re.compile(r'^\.?codecov\.ya?ml$'),
    'composer': re.compile(r'^composer\.(json|lock)$'),
    'docker': re.compile(r'^(docker-(cloud|compose.*)\.ya?ml|'
                         r'\.dockerignore|Dockerfile)$'),
    'editorconfig': re.compile(r'^\.editorconfig$'),
    'eslint': re.compile(_rc_ignore.format('eslint')),
    'firebase': re.compile(r'^(\.?fire(base(\.json|rc)|store\.rules))$'),
    'git': re.compile(r'^(\.git(ignore|attributes|config|'
                      r'modules|keep)|\.mailmap)$'),
    'gradle': re.compile(r'^.+\.gradle(\.kts)?$'),
    'grunt': re.compile(r'^[Gg]runtfile\.(babel\.js|[jtl]s|coffee)$'),
    'gulp': re.compile(r'^[Gg]ulpfile\.(babel\.js|[jtl]s|coffee)$'),
    'heroku': re.compile(r'^(Procfile|app.json)$'),
    'jenkins': re.compile(r'^Jenkinsfile$'),
    'license': re.compile(r'^(LICEN[CS]E|COPYING).*$', re.I),
    'log': re.compile(r'^.+\.log$', re.I),
    'manifest': re.compile(r'^(manifest\.(mf|json|in)|'
                           r'AndroidManifest\.xml|'
                           r'.*\.webmanifest)$', re.I),
    'maven': re.compile(r'^(pom\.xml|.*\.pom)$'),
    'nginx': re.compile(r'^.*nginx\.conf$'),
    'node': re.compile(r'^package\.json$'),
    'npm': re.compile(r'^(\.npm(ignore|rc)|'
                      r'npm-shrinkwrap\.json|'
                      r'package-lock\.json)$'),
    'nuget': re.compile(r'^(.*\.nuspec|nuget\.config)$', re.I),
    'pip': re.compile(r'^(.*requirements.*\.(pip|txt)|'
                      r'Pipfile(\.lock)?|poetry\.lock|'
                      r'pyproject\.toml)$'),
    'readme': re.compile(r'^README.*$', re.I),
    'robots': re.compile(r'^robots\.txt$'),
    'rollup': re.compile(r'^rollup.*\.config\..+$'),
    'stylelint': re.compile(_rc_ignore.format('stylelint')),
    'tern': re.compile(r'^\.tern-(project|config)$'),
    'travis': re.compile(r'^\.travis\.yml$'),
    'vagrant': re.compile(r'^Vagrantfile$'),
    'webpack': re.compile(r'^webpack.*\.config\..+$'),
    'yarn': re.compile(r'^(\.yarn(ignore|rc)|yarn.lock)$'),
}

#: A list of supported filetypes.
SUPPORTED_FTS = [
    'actionscript',
    'ant',
    'applescript',
    'arduino',
    'asciidoc',
    'asm',  # (includes fasm, nasm, mips)
    'blade',
    'c',
    'clojure',
    'cmake',
    'coffee',
    'config',  # (includes cfg, conf, dosini, jproperties)
    'cpp',
    'crystal',
    'cs',
    'css',
    'csv',
    'd',
    'dart',
    'diff',
    'django',  # (includes htmldjango)
    'dosbatch',
    'dotnet',  # (includes asp, aspvbs, vb, vbnet)
    'elixir',
    'elm',
    'erlang',
    'eruby',
    'glsl',
    'go',
    'graphql',
    'groovy',
    'haml',
    'haskell',
    'haxe',
    'hcl',
    'html',
    'ipynb',
    'iss',
    'java',
    'javascript',
    'jinja',
    'json',  # (includes json5)
    'jsp',
    'jsx',  # (includes javascript.jsx)
    'julia',
    'kotlin',
    'less',
    'liquid',
    'lisp',
    'llvm',
    'log',  # (includes httplog, log4j, messages, syslog)
    'ls',
    'lua',
    'make',
    'markdown',
    'matlab',
    'mustache',  # (includes html.mustache)
    'nim',
    'nix',
    'nsis',
    'ocaml',
    'octave',
    'pascal',  # (includes delphi)
    'perl',  # (includes perl6)
    'php',
    'plantuml',
    'postcss',
    'proto',
    'ps1',
    'pug',
    'python',
    'r',
    'rst',
    'ruby',
    'rust',
    'sass',  # (includes scss)
    'scala',
    'sh',  # (includes awk, fish, sed, zsh)
    'sql',
    'stylus',
    'svelte',
    'svg',
    'swift',
    'tcl',
    'tex',  # (includes bib, plaintex)
    'textile',
    'toml',
    'twig',  # (includes html.twig)
    'typescript',
    'verilog',  # (includes systemverilog)
    'vhdl',
    'vim',
    'vue',
    'xml',
    'yaml'
] + list(SPECIAL_FTS)

__all__ = ['CLIENT_ID', 'SUPPORTED_FTS', 'SPECIAL_FTS']
