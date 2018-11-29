import re

rc = lambda n: '^([.]?{0}rc([.]js(on)?|[.]ya?ml)?|' \
               '{0}[.]config[.]js|[.]{0}ignore)$'.format(n)

CLIENT_ID = '492721776145596416'

SPECIAL_FTS = {
    'ansible': re.compile(r'^(ansible[.]cfg|site.ya?ml|hosts)$'),
    'apache': re.compile(r'^((.+[.])*(apache|httpd)[.]conf|[.]htaccess)$'),
    'appveyor': re.compile(r'^[.]?appveyor[.]ya?ml$'),
    'babel': re.compile(r'%s' % rc('babel')),
    'bower': re.compile(r'^([.]bowerrc|bower[.]json)$'),
    'browserslist': re.compile(r'^[.]?browserslist(rc|)$'),
    'bundler': re.compile(r'^(Gemfile([.]lock)|[.]gemspec)$'),
    'cargo': re.compile(r'^Cargo[.](toml|lock)$'),
    'circleci': re.compile(r'^circle[.]yml$'),
    'codeclimate': re.compile(r'^[.]codeclimate[.](ya?ml|json)$'),
    'codecov': re.compile(r'^[.]?codecov[.]ya?ml$'),
    'composer': re.compile(r'^composer[.]json$'),
    'docker': re.compile(r'^[Dd]ocker(file|-compose[.]ya?ml)$'),
    'editorconfig': re.compile(r'^[.]editorconfig$'),
    'eslint': re.compile(r'%s' % rc('eslint')),
    'git': re.compile(r'^[.]git(ignore|attributes|modules|config)$'),
    'gradle': re.compile(r'^.+[.]gradle$'),
    'grunt': re.compile(r'^[Gg]runtfile[.](babel[.]js|[jtl]s|coffee)$'),
    'gulp': re.compile(r'^[Gg]ulpfile[.](babel[.]js|[jtl]s|coffee)$'),
    'heroku': re.compile(r'^Procfile$'),
    'jenkins': re.compile(r'^Jenkinsfile$'),
    'license': re.compile(r'^(LICENSE|COPYING)([.].+)?$', re.I),
    'log': re.compile(r'^.+[.]log$', re.I),
    'manifest': re.compile(r'^(manifest[.](mf|json)|'
                           'AndroidManifest[.]xml|'
                           '.*[.]webmanifest)$', re.I),
    'maven': re.compile(r'^(pom[.]xml|.*[.]pom)$'),
    'nginx': re.compile(r'^(.+[.])*nginx[.]conf$'),
    'node': re.compile(r'^package[.]json$'),
    'npm': re.compile(r'^([.]npm(ignore|rc)|'
                      'npm-shrinkwrap[.]json|'
                      'package-lock[.]json)$'),
    'nuget': re.compile(r'^(.*[.]nuspec|nuget[.]config)$', re.I),
    'pip': re.compile(r'^requirements([[.]-].+)*[.](pip|txt)$'),
    'readme': re.compile(r'^README([.].+)?$', re.I),
    'robots': re.compile(r'^robots[.]txt$', re.I),
    'rollup': re.compile(r'^rollup[.]config[.]js$'),
    'stylelint': re.compile(r'%s' % rc('stylelint')),
    'tern': re.compile(r'^[.]tern-(project|config)$'),
    'travis': re.compile(r'^[.]travis[.]yml$'),
    'vagrant': re.compile(r'^Vagrantfile$'),
    'webpack': re.compile(r'^webpack[.]config[.]js$'),
    'yarn': re.compile(r'^([.]yarn(ignore|rc)|yarn.lock)$'),
}

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
    'go',
    'graphql',
    'groovy',
    'haml',
    'haskell',
    'haxe',
    'html',
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
    'log',  # (includes httplog, log4j, messages, syslog)
    'ls',
    'lua',
    'make',
    'markdown',
    'matlab',
    'mustache',  # (includes html.mustache)
    'nix',
    'nsis',
    'ocaml',
    'octave',
    'pascal',  # (includes delphi)
    'perl',  # (includes perl6)
    'php',
    'plantuml',
    'postcss',
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
    'svg',
    'swift',
    'tcl',
    'tex',  # (includes bib, plaintex)
    'textile',
    'toml',
    'twig',  # (includes html.twig)
    'typescript',
    'verilog',
    'vhdl',
    'vim',
    'vue',
    'xml',
    'yaml'
] + list(SPECIAL_FTS)

__all__ = ['CLIENT_ID', 'SUPPORTED_FTS', 'SPECIAL_FTS']

