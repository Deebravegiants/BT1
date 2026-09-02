This confirms the finding: the docs explicitly tell developers that `data.shop` is "the shop domain of the webhook" and to use it as the tenant identifier (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), yet that value is never covered by the HMAC signature. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so `Utils::HmacValidator.validate` verifies solely the body bytes against the `hmac-sha256` header. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers used by `ShopifyAPI::Webhooks::Registry.process` and handed to app handlers as `WebhookMetadata` are never bound to the HMAC, so any of them can be forged independently of a legitimately-signed body.

### Finding Description
`Request#to_signable_string` is defined as: [3](#0-2) 

and `Registry.process` accepts the request as valid purely based on that body signature: [4](#0-3) 

`request.shop` is read straight from the `shop-domain` (or `x-shopify-shop-domain`) header with no cross-check against the body or any registered session: [5](#0-4) 

Because the app's `client_secret` (`Context.api_secret_key`) is a single secret shared across every shop that installs the app, an attacker who controls their own installed shop can capture (or construct, since payload contents like a plain `{}` or their own webhook body are known/predictable for many topics) a `(raw_body, hmac)` pair that validates correctly, then replay it directly to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` only recomputes the HMAC over `@raw_body`, so this forged header sails through, and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the attacker-chosen (victim) shop instead of the shop that actually owns the token used to compute the HMAC. This breaks the identity binding the docs assume holds: `HMAC-verified sender == data.shop`.

The security model here fails to check `hmac-covers(shop) == true` before letting `data.shop` drive tenant-scoped logic — the equality that should hold, `shop-domain header == shop cryptographically bound in signable content`, does not, since only the body is signed.

### Impact Explanation
Per the library's own documentation, `data.shop` is meant to be trusted by the app to key tenant-specific actions (job enqueuing, database writes, GDPR data requests/redactions such as `customers/redact` and `shop/redact`, which are the library's own mandatory topics). An attacker forging this field lets them make the app perform actions attributed to (i.e., cross-tenant on behalf of) a shop they do not control — including triggering a merchant's mandatory-topic handler (e.g., `customers/data_request`, `customers/redact`, `shop/redact`) or polluting another tenant's data pipeline with attacker-controlled payloads, all without any credential belonging to the victim shop. This matches the Critical/High "cross-tenant access" impact class, since the tenant boundary (`shop`) that the gem's own webhook contract is built around is not authenticated.

### Likelihood Explanation
The prerequisite is modest: the attacker only needs their own installed instance of the same app (a normal, unprivileged action for any Shopify merchant/developer who can install a public or unlisted app), from which they can obtain a validly HMAC-signed `(body, signature)` pair (e.g., from a real webhook delivery to their own shop, or by using a body they fully control such as `{}` combined with any topic whose handler doesn't depend on body contents). They then replay that exact body+signature to the app's public webhook endpoint with a spoofed `shopify-shop-domain` header value. No access token, TLS interception, or victim credential is required — only knowledge of the app's public webhook URL, which is normally disclosed in the app's own OAuth/webhook registration configuration.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) headers as part of the HMAC-signed content, or at minimum require callers to independently authenticate the `shop-domain` header against a known/registered shop (e.g., by checking it against sessions on file) before trusting `WebhookMetadata#shop` in `Registry.process`. Note that Shopify's actual webhook delivery HMAC (`X-Shopify-Hmac-Sha256`) is computed only over the raw body per Shopify's own webhook spec, so any real fix likely requires `Registry.process` to additionally validate `shop-domain` against a shop known to have an active/registered webhook subscription (e.g. cross-referencing an app-side session store) rather than trusting the header value outright, since the header itself cannot be feasibly added to the signature without deviating from Shopify's documented HMAC computation.

### Proof of Concept
1. Attacker installs the target app on their own controlled development store `attacker.myshopify.com`, obtaining legitimate webhook deliveries signed with the app's single, shared `client_secret`.
2. Attacker captures one such delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — this pair validates for any shop because the secret is shared per-app, not per-shop.
3. Attacker POSTs directly to the app's public webhook route (e.g. `/callback/orders/create`) with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (`= B`) against `H` — this passes.
5. `Registry.process` looks up the handler for the topic and invokes it with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, even though the request was never authorized by or for `victim-shop.myshopify.com`. [4](#0-3)

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
