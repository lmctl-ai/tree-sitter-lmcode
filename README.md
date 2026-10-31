# tree-sitter-lmcode

MIT-licensed tree-sitter syntax grammar for **lmcode**, the typed language inside
lmscript `_lmcode_` blocks. Copyright Lattice Systems LLC. Maintainer/sync owner:
the lmctl lmscript team (`lmctl-ai`). This parser is for analysis and editor tools;
it does not replace the compiler or resolve schemas, overloads, types or effects.

## Build and test

Use Node 24, a C compiler, Python 3 and tree-sitter-cli **0.27.1**. Install the CLI
in a private prefix, then put that prefix's node_modules/.bin on PATH. If npm's
install-script policy leaves the binary uninstalled, run the package's install.js
from its own directory. No global install is needed.

Run `tree-sitter generate`, `tree-sitter test --rebuild`, then:

~~~sh
python3 scripts/conformance.py
python3 scripts/negative.py
python3 scripts/incremental.py
python3 scripts/scanner-limits.py
python3 scripts/controls.py
~~~

TREE_SITTER may name an absolute private CLI path. GitHub Actions runs these gates
on Ubuntu and macOS, checks scanner warnings and checks generated-file freshness.
The generated src/parser.c, grammar.json and node-types.json are committed; native
consumers compile parser.c plus scanner.c and do not need Node or the generator.
No package publication or tagged release is part of this repository's setup.

## Syntax and node contract

Typed fn declarations, annotations and implements clauses; locals and assignments;
if/else, while, range/collection loops, switch arms, break/continue; ordinary calls,
method chains and enum/member spelling; precedence-aware expressions; qw/qi/qf,
map entries using `=>`, plain/dedented/queued heredocs and json heredoc literals.

`$return`, `$return.name` and `$return[expression]` are assignment targets only.
The index's string type remains a compiler check. Return reads, declarations,
nested paths and compound writes are refused. These forms are implemented in the
pinned mono source (a9df5a8b), although the separately pinned EBNF still describes
published compiler 0.2.444 and marks them planned. Executable block results,
load_schema and reverse templates are outer-language/runtime work, not syntax
features this grammar claims to ship. See SOURCE-PINS.json and DIVERGENCES.md.

Important named nodes: function_declaration (name, return_type, body), annotation,
implements_clause (interface), call_expression (function), member_expression,
map_entry (key/value), return_assignment (target/value), and splice (expression).
Splices parse LMScript expressions, including nested objects, indexing, tuples,
conditions, calls, raw/path/triple strings and nested formatted strings. Assignment,
parallel and data-block expressions are excluded from splice fields.

Heredoc literals expose a heredoc_start at the expression position. Their raw
heredoc_body tokens are named extras in source order: pair them with starts using
the same FIFO rule as the compiler. Each body includes the next-line separator and
its exact closing tag, so text inside it (including `${...}` and outer block markers)
is not parsed as code. A visible zero-width end_of_file sentinel makes unresolved
queued bodies fail closed rather than disappear during error recovery. Scanner
state includes the pending queue and splice phase and is serialized for edits.

## Pinned conformance

The checked-in corpus contains **127 extracted bodies**: 3 from mono examples,
14 from lmok rule packs and 110 from lmcode-cpp sample-suite programs. All source
files are inventoried, including files with no lmcode block; the importer uses the
authoritative outer Lexer rather than a delimiter-only regex. It never executes a
script or queries a host. Body/source hashes, block numbers and original line
numbers are in test/fixtures/conformance/manifest.json. CI needs no private checkout.

The 39 tree-sitter corpus cases, 21 syntax-refusal cases, combined feature/splice
fixtures and incremental/scanner stress gates complement those real bodies.
Mutations remove serialized heredoc state, map-entry arrows, dedent recognition,
splice-phase isolation, EOF enforcement and qw scanning. No changed assertions or
failed builds count as successful controls. Current lmok bodies contain no `=>`;
that control therefore uses the real C++ map-literal sample and a separate
rule-pack-shaped map fixture, rather than claiming an upstream lmok failure.

Refresh intentionally with scripts/import-corpus.mjs and four private/read-only
checkouts (mono, lmok, lmcode-cpp, lmcode spec). Review SOURCE-PINS.json and fixture
changes together. S3's 500-document semantic differential harness and S4/S5 lmok
registration/injection are separate landing slices; this S2 repository does not
claim those integrations are complete.
