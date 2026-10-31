# Syntax/semantic boundary and known divergences

Source pins are in SOURCE-PINS.json. The handwritten compiler remains authoritative.
These classes are explicit inputs to the planned S3 differential allowlist, not a
claim of arbitrary accept/reject equivalence or a bypass in this repo's syntax gates.

| Class | Compiler vs this grammar | Reason / analysis discipline |
| --- | --- | --- |
| Schema names, types, overloads, interfaces | Compiler rejects unknown or incompatible declarations/calls; grammar accepts their structure | Schema-semantic checking is excluded. Do not infer that a clean tree is executable. |
| Scope/control restrictions | Compiler checks reserved binding names, redeclarations, break/continue placement, annotation/interface agreement, fn return type/position and effectless expression statements | Grammar enforces top-level fn and final syntactic return placement, but not typing or binding/control validity. |
| Contextual qw/qi/qf/json | Compiler consults local/user/schema bindings before choosing literals; grammar gives literal-shaped syntax a structural interpretation and permits ordinary calls where possible | A literal node is not proof of an unshadowed constructor; use compiler/schema information for such claims. |
| Numeric ranges and string/path validation | Compiler rejects int/finite bounds, some outer Unicode escapes and invalid path-literal values; grammar recognizes their syntax | No constant evaluation, Unicode-scalar decoding or platform path policy is implemented here. Ordinary lmcode floats still require digits.digits; qi/qf word forms are distinct. |
| Heredoc dedent semantics / JSON content | Compiler rejects mixed removed indentation and invalid JSON/JSONC in json heredocs; grammar preserves raw bodies | The scanner checks tag identity, queue order and closer layout, not the decoded body value. |
| Member access | Compiler permits bare enum constants and typed method chains, rejecting unsupported field reads; grammar exposes member_expression uniformly | Resolve enum/object distinctions semantically; there is no schema-aware parser branch. |
| Scanner serialization capacity | Compiler permits arbitrarily long tags/queues; this scanner refuses a pending queue whose serialized representation would exceed tree-sitter's 1024-byte state buffer | Refusal produces parse errors, never a truncated tag or a clean wrong tree. Tests cover 301-byte tags, 80 queued bodies and capacity refusal. |
| Versioned EBNF | Pinned spec EBNF targets 0.2.444 and omits planned return lvalues; pinned mono main implements them | Grammar follows the newer source for return assignments. This discrepancy is documented, not silently treated as an EBNF conformance pass. |

LMScript splice fields are parsed expressions, not a regex stopping at the first
brace. A clean field tree still does not certify called functions, literal escape
values or compiler field-value conversion. Hash comments are valid in lmcode;
slash comments are accepted only within LMScript splice fields.
