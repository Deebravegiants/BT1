### Title
Webhook shop identity is not bound to the HMAC, allowing shop-domain spoofing / cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw body bytes with HMAC, while the `shop` (and `topic`/`webhook-id`) values used by `ShopifyAPI::Webhooks::Registry.process` to identify *which tenant* the event belongs to are taken from unauthenticated HTTP headers that are never part of the signed material. This breaks the equality that should hold: `hmac_verified_bytes == bytes_that_determine_the_tenant`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`, i.e. the body, and compares it to the `hmac` header value: [2](#0-1) 

`Registry.process` then trusts `request.shop` (sourced from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not covered by the HMAC) to build the `WebhookMetadata` that is handed to the app's handler as the tenant identity for the event: [3](#0-2) [4](#0-3) 

`Context.api_secret_key` (the app's client secret) is a single value shared by *all* shops that install the app — it is not shop-specific: [5](#0-4) 

Because the same secret is used to sign every shop's webhooks, and the signature covers only the body, any actor who can install the public/unprivileged app on their own store (a normal, unprivileged action any Shopify merchant can take) receives genuinely Shopify-signed `(body, hmac)` pairs for their own shop. That attacker can then replay the identical body+HMAC to the target app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` forwards `shop: request.shop` — the attacker-controlled, unauthenticated header — into `WebhookMetadata`, which downstream app logic uses to look up or mutate the "corresponding" tenant's data/session.

This is the direct analog of the `AuraVault::claim` root cause: the report's bug was "fee amount acted upon but not deducted/bound in the arithmetic used to determine the recipient's due amount"; here the bug class instructed by the rules is "a field acted on but not covered by the HMAC" — the `shop` field is acted upon (used as the tenant key) but is not included in the value that the HMAC actually authenticates.

### Impact Explanation
This enables cross-tenant webhook injection: an attacker with no privileges beyond installing the app on their own store can forge/replay webhook events that the receiving application will attribute to an arbitrary victim shop domain, because the library's HMAC validation gives no guarantee that the `shop` value processed by `Registry.process`/`WebhookMetadata` is the same shop that produced the signed bytes. Depending on how the host app trusts this metadata (e.g., to select which merchant's records to update, uninstall, or resync), this crosses the tenant boundary — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the target app on an attacker-controlled store — normal, unprivileged, self-service Shopify functionality — to obtain a validly signed webhook body+HMAC, and (2) sending an HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header, which requires no credentials, tokens, or secrets. No privileged access, `api_secret_key`, or social engineering is needed, making this practically reachable by any unprivileged internet user who is also allowed to install the app.

### Recommendation
Bind the tenant identity into the material that is actually authenticated. At minimum:
- Reject webhook processing unless the `shop` obtained from `request.shop` matches a shop the app has verified/installed via its own authenticated session store lookup, rather than trusting the header value as-is.
- Where feasible, include `shop`/`topic`/`webhook-id` in the signable string (or otherwise cryptographically bind them), so `HmacValidator.validate` fails if any of these headers are tampered with independently of the body.
- Document explicitly in `Registry.process`/`WebhookMetadata` that `shop` is unauthenticated header data and must be cross-checked by the host app against its own session/shop registry before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (computed by Shopify over `B` using the shared `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the same body `B` and the same `H` to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the request; `to_signable_string` returns `B` unchanged (`lib/shopify_api/webhooks/request.rb:35-38`).
4. `HmacValidator.validate` recomputes HMAC over `B` with `Context.api_secret_key` and it matches `H` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) — validation succeeds despite the shop header being forged.
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-supplied `victim.myshopify.com` value (`lib/shopify_api/webhooks/registry.rb:198-199`), and the app's handler processes the event as if it originated from the victim's shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```

**File:** lib/shopify_api/context.rb (L78-79)
```ruby
        @api_key = api_key
        @api_secret_key = api_secret_key
```
