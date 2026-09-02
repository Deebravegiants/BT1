### Title
Webhook `shop` (and `topic`/`webhook-id`) Identity Fields Are Not Covered by the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature that `Webhooks::Registry.process` validates is computed over the raw request body only. The header that binds a webhook to a specific merchant is never included in the signed bytes, so an attacker who has legitimately obtained one valid `(body, hmac)` pair for their own shop can replay it with a different `shop` header and have it accepted as an authentic webhook for another tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and the `shop` accessor is read straight from an unauthenticated header: [2](#0-1) 

`Webhooks::Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)`, which in turn calls `validate_signature`, comparing `compute_signature(verifiable_query.to_signable_string, secret)` against the header-supplied `hmac`: [3](#0-2) [4](#0-3) 

Because `to_signable_string` never mixes in `shop`, `topic`, or `webhook_id`, the HMAC only proves that the body bytes were signed with the app's `client_secret` at some point — it proves nothing about which shop, topic, or webhook the body was meant for. The `shop` value that `handler.handle` receives and that the host application will use to look up per-tenant state is bound to the identity `verified-body == signed-body`, but the actual identity check the host application relies on is `shop-header == originating-tenant`, which the gem does not enforce anywhere. This breaks the equality that should hold: `HMAC-covered bytes == bytes that determine tenant identity`.

Any Shopify app installed on an attacker-controlled shop will legitimately receive real, correctly-HMAC'd webhooks for that shop (e.g. `orders/create`). The attacker captures one such `(raw_body, hmac)` pair, then replays it to the same app's webhook endpoint with the `shopify-shop-domain`/`x-shopify-shop-domain` header changed to a victim shop domain (and optionally a different `shopify-topic` header, which is also unsigned). `HmacValidator.validate` still passes because the body/hmac pair is genuinely valid, and `Registry.process` dispatches to the handler with `WebhookMetadata.new(... shop: request.shop ...)` reporting the victim's shop: [5](#0-4) 

If the host application uses this `shop` value to select a session/tenant record (a common and documented pattern for this gem's webhook handlers), the attacker can inject fabricated "events" attributed to any shop domain, achieving cross-tenant impact without ever needing that tenant's access token or secret.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem's own webhook verification primitive does not bind the merchant identity to the cryptographic proof, so a party with valid credentials for shop A can forge events on behalf of shop B purely by manipulating unsigned headers. This matches the Critical "cross-tenant access" impact category — an attacker can make the host application act on data as though it originated from a shop that never sent it, using only their own legitimate app installation.

### Likelihood Explanation
Any merchant who installs the vulnerable app can trivially trigger a real webhook for their own store, capture the `(raw_body, hmac)` pair via their own webhook endpoint logs, and replay it with a rewritten `shop`/`topic` header — no access to the app's `client_secret`, no interception of TLS, and no privileged account are required. The only inputs needed (a legitimately-received webhook and control over headers on a replayed HTTP request) are available to any unprivileged internet user who installs the app on a shop they control.

### Recommendation
Include the identity-binding fields (`shop-domain`, `topic`, and ideally `webhook-id`) in the bytes that are HMAC-verified, or otherwise cryptographically bind them to the signed payload, rather than trusting them as bare, unsigned headers. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop domain so that `Utils::HmacValidator.validate` cannot succeed for a body/shop combination that Shopify did not actually sign together.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger a real event (e.g., create an order) so Shopify sends a legitimate webhook:
   - Headers: `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid-hmac-of-body>`
   - Body: `{"id": 123, ...}`
2. Capture this `(raw_body, hmac)` pair from the attacker's own endpoint logs.
3. Replay the exact same request to the app's webhook endpoint, but change only the header:
   - `shopify-shop-domain: victim.myshopify.com`
   - Keep the same `raw_body` and `shopify-hmac-sha256` value.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only, matches the replayed `hmac`, and returns `true`.
5. `Webhooks::Registry.process` invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: {...}, ...)`, causing the host application to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
