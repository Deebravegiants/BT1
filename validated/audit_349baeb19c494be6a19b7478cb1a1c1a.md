No vulnerability found for this question.

The code in `AbilitySet::polymorphic_abilities` correctly filters out phantom type parameters before folding their abilities into the intersection, using `.filter(|(_, is_phantom)| !is_phantom)` [1](#0-0)  This is the intended, correct behavior — phantom type parameters are not required to satisfy the ability constraints of the declaring struct, and the `filter` step properly excludes them from the `fold`/`intersect` computation regardless of what abilities are supplied for that type argument.

The `Ability::required_by` mapping (`Store -> {Store, Key}`) is also correct by design: it is the mathematical inverse of `requires()`, where `Key.requires() == Store` and `Store.requires() == Store`, so both `Store` and `Key` must appear in `Store.required_by()` [2](#0-1) . This is not a bug — it is the standard ability-inference rule used throughout Move's type system.

The premise of the question depends entirely on a hypothetical, unverified bug in "a bytecode verifier" that would mark a phantom type parameter as non-phantom when computing `declared_phantom_parameters`. No such verifier bug is shown to exist in this file or referenced concretely — `ability.rs` only consumes whatever `declared_phantom_parameters`/`type_arguments` it is given and processes them correctly. Since the review scope requires tracing a real, demonstrable unprivileged-input path across a custody boundary, and this finding instead speculates about an unproven defect in an unrelated component (the bytecode verifier) to make an otherwise-correct function misbehave, it does not meet the bar for a valid custody-impacting vulnerability in this file.

### Citations

**File:** third_party/move/move-core/types/src/ability.rs (L43-63)
```rust
    /// For a struct with ability `a`, each field needs to have the ability `a.requires()`.
    /// Consider a generic type Foo<t1, ..., tn>, for Foo<t1, ..., tn> to have ability `a`, Foo must
    /// have been declared with `a` and each type argument ti must have the ability `a.requires()`
    pub fn requires(self) -> Self {
        match self {
            Self::Copy => Ability::Copy,
            Self::Drop => Ability::Drop,
            Self::Store => Ability::Store,
            Self::Key => Ability::Store,
        }
    }

    /// An inverse of `requires`, where x is in a.required_by() iff x.requires() == a
    pub fn required_by(self) -> AbilitySet {
        match self {
            Self::Copy => AbilitySet::EMPTY | Ability::Copy,
            Self::Drop => AbilitySet::EMPTY | Ability::Drop,
            Self::Store => AbilitySet::EMPTY | Ability::Store | Ability::Key,
            Self::Key => AbilitySet::EMPTY,
        }
    }
```

**File:** third_party/move/move-core/types/src/ability.rs (L235-246)
```rust
        let abs = type_arguments
            .zip(declared_phantom_parameters)
            .filter(|(_, is_phantom)| !is_phantom)
            .map(|(ty_arg_abilities, _)| {
                ty_arg_abilities
                    .into_iter()
                    .map(|a| a.required_by())
                    .fold(AbilitySet::EMPTY, AbilitySet::union)
            })
            .fold(declared_abilities, |acc, ty_arg_abilities| {
                acc.intersect(ty_arg_abilities)
            });
```
