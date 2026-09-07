# [H] Plate allows arbitrary DOM attributes in element.attributes and leaf.attributes

## Summary
Severity: High
Advisory: GHSA-73rg-f94j-xvhx
CVE: CVE-2024-47061
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-09-20
Source: https://github.com/advisories/GHSA-73rg-f94j-xvhx
Type: github-advisory

## Affected
- npm: `@udecode/plate-core` — affected >=37.0.0 <38.0.6
- npm: `@udecode/plate-core` — affected >=22.0.0 <36.5.9
- npm: `@udecode/plate-core` — affected >=0 <21.5.1

## Details
### Impact
One longstanding feature of Plate is the ability to add custom DOM attributes to any element or leaf using the `attributes` property. These attributes are passed to the node component using the `nodeProps` prop.

Note: The `attributes` prop that is typically rendered alongside `nodeProps` is unrelated.

```ts
[{
  type: 'p',
  attributes: { 'data-my-attribute': 'This will be rendered on the paragraph element' },
  children: [{
    bold: true,
    attributes: { 'data-my-attribute': 'This will be rendered on the bold leaf element' },
    text: 'Bold text',
  }],
}]
```

```tsx
const ParagraphElement = ({ attributes, nodeProps, children }) => (
  <p
    {...attributes}
    {...nodeProps} // Arbitrary DOM attributes are injected here
  >
    {children}
  </p>
);

const BoldLeaf = ({ attributes, nodeProps, children }) => (
  <strong
    {...attributes}
    {...nodeProps} // Arbitrary DOM attributes are injected here
  >
    {children}
  </strong>
);
```

It has come to our attention that this feature can be used for malicious purposes, including cross-site scripting (XSS) and information exposure (specifically, users' IP addresses and whether or not they have opened a malicious document).

Note that the risk of information exposure via `attributes` is only relevant to applications in which web requests to arbitrary URLs are not ordinarily allowed. Plate editors that allow users to embed images from arbitrary URLs, for example, already carry the risk of leaking users' IP addresses to third parties.

All Plate editors using an affected version of `@udecode/plate-core` are vulnerable to these information exposure attacks via the `style` attribute and other attributes that can cause web requests to be sent. 

In addition, whether or not a Plate editor is vulnerable to cross-site scripting attacks using `attributes` depends on a number of factors. The most likely DOM attributes to be vulnerable are `href` and `src` on links and iframes respectively. Any component that spreads `{...nodeProps}` onto an `<a>` or `<iframe>` element and does not later override `href` or `src` will be vulnerable to XSS.

```tsx
<a
  href={sanitizedHref}
  {...attributes}
  {...nodeProps} // Definitely vulnerable to XSS since `href` can be overridden
>
```

```tsx
<a
  {...attributes}
  {...nodeProps} // Probably not vulnerable to XSS via `href`
  href={sanitizedHref}
>
```

```tsx
<a
  {...attributes}
  {...nodeProps} // May be vulnerable to XSS via `href` if `href` is sometimes omitted from `sanitizedLinkProps`
  {...sanitizedLinkProps}
>
```

React does not allow passing a string to event handler props like `onClick`, so these are unlikely (but not impossible) to be vulnerable.

The attack surface is larger for users running older browsers, which may be vulnerable to XSS in DOM attributes that are less dangerous (although still vulnerable to information exposure) in modern browsers such as `style` or `background`.

Potential attack vectors for delivering malicious Slate content to users include:

- Opening a malicious document stored on the server
- Pasting a malicious Slate fragment into a document
- Receiving malicious Slate operations on a collaborative document

### Patches
In patched versions of Plate, we have disabled `element.attributes` and `leaf.attributes` for most attribute names by default, with some exceptions including  `target`, `alt`, `width`, `height`, `colspan` and `rowspan` on the link, image, video, table cell and table header cell plugins.

If this is a breaking change for you, you can selectively re-enable `attributes` for certain plugins as follows. Please carefully research and assess the security implications of any attribute you allow, as even seemingly innocuous attributes such as `style` can be used maliciously.

#### Plate >= 37

For custom plugins, specify the list of allowed attribute names in the `node.dangerouslyAllowAttributes` plugin configuration option.

```ts
const ImagePlugin = createPlatePlugin({
  key: 'image',
  node: {
    isElement: true,
    isVoid: true,
    dangerouslyAllowAttributes: ['alt'],
  },
});
```

To modify an existing plugin, use the `extend` method.

```ts
const MyImagePlugin = ImagePlugin.extend({
  node: {
    dangerouslyAllowAttributes: ['alt'],
  },
});
```

#### Plate < 37

Note that the patch has been backported to versions `@udecode/plate-core@21.5.1` and `@udecode/plate-core@36.5.9` only.

For custom plugins, specify the list of allowed attribute names in the `dangerouslyAllowAttributes` plugin configuration option.

```ts
const createImagePlugin = createPluginFactory({
  key: 'image',
  isElement: true,
  isVoid: true,
  dangerouslyAllowAttributes: ['alt'],
});
```

To modify an existing plugin, pass `dangerouslyAllowAttributes` to the plugin factory.

```ts
createImagePlugin({
  dangerouslyAllowAttributes: ['alt'],
});
```

### Workarounds

If you are unable to upgrade to any of the patched versions, you should use a tool like [`patch-package`](https://www.npmjs.com/package/patch-package) or [`yarn patch`](https://yarnpkg.com/cli/patch) to remove the logic from `@udecode/plate-core` that adds `attributes` to `nodeProps`.

This logic can be found in the `getRenderNodeProps` function and looks something like this. The entire `if` statment can safely be removed.

```ts
  if (!newProps.nodeProps && attributes) {
    newProps.nodeProps = attributes;
  }
```

After applying the patch, be sure to test its effectiveness by rendering a Slate value containing an `attributes` property on some element.

```ts
[{
  type: 'p',
  attributes: { 'data-vulnerable': true },
  children: [{ text: 'My paragraph' }],
}]
```

If the patch was successful, the `data-vulnerable="true"` attribute should not be present on any DOM element when the Plate editor is rendered in the browser.

## References
- https://github.com/udecode/plate/security/advisories/GHSA-73rg-f94j-xvhx
- https://nvd.nist.gov/vuln/detail/CVE-2024-47061
- https://github.com/udecode/plate/commit/16df6074edac22d56c60e0283eae0740230401c9
- https://github.com/udecode/plate
- https://www.npmjs.com/package/patch-package
- https://yarnpkg.com/cli/patch
