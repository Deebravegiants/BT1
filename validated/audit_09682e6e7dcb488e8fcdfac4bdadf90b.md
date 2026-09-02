### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header (`shopify-shop-domain`/`x-shopify-shop-domain`) that is never included in the bytes the HMAC signs, while `topic`, `webhook_id`, and `api_version` are equally unauthenticated. `Registry.process` verifies only that the *raw body* is HMAC-valid, then trusts the header-derived `shop` and passes it straight to the app's `WebhookHandler#handle`. This breaks the identity binding `shop_verified == shop_used_by_handler`.

### Finding Description
`Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are completely outside that signed string: [3](#0-2) 

`Registry.process` validates the HMAC (i.e., proves the body came from Shopify using the app's `client_secret`) and then unconditionally forwards `request.shop` — an unauthenticated header — as the tenant identity to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no cryptographic linkage to the verified payload: [5](#0-4) 

The identity binding the report's bug class targets is: **`hmac_signed_bytes == bytes_that_determine_the_tenant`**. Here that equality is false — `hmac_signed_bytes = raw_body` while `tenant = header["shopify-shop-domain"]`, a field the signature never covers. Since Shopify signs every webhook for every shop that installed a given app with the *same* `client_secret` (this gem intentionally supports only a single global secret, with an optional `old_api_secret_key` for rotation — see `HmacValidator.validate`), any shop that has the app installed can capture a legitimately-signed webhook delivered to *its own* store and replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. Because the signature check only revalidates the body bytes (identical to the original), the request still passes `Utils::HmacValidator.validate`, and the handler executes believing the event originated from the victim tenant.

### Impact Explanation
This is a cross-tenant identity-binding bypass at the credential-verification boundary the gem itself implements (`HmacValidator`/`Webhooks::Registry`). An attacker who is a legitimate merchant of the same multi-tenant app can:
- Forge `app/uninstalled`, `shop/redact`, or other mandatory/topic-specific webhooks attributed to a victim shop, causing the app to delete/revoke data or perform tenant-scoped side effects for a shop the attacker does not control.
- Inject arbitrary attacker-controlled body content (as long as it satisfies the app's own body validation, if any) under a spoofed victim `shop` value, since `shop` is decoupled from the HMAC-checked payload entirely.

This matches the "Critical - cross-tenant access" category: the confidentiality/integrity boundary between tenants of the same app is broken using only unprivileged access (being any merchant who installed the app), no leaked secret required.

### Likelihood Explanation
Likelihood is High for any app using `ShopifyAPI::Webhooks::Registry.process` as documented: the attack requires no `client_secret`, no access token, and no privileged access — only that the attacker operates their own store with the vulnerable app installed (or can otherwise capture one valid webhook delivery, e.g. from a public app listing), then replays the raw body against the endpoint with a rewritten `shop-domain` header, which is normal HTTP tooling with no cryptographic material needed.

### Recommendation
- Include `shop` (and ideally `topic`, `webhook_id`) as part of the HMAC-signed material, or independently verify the `shop` header against a trusted, previously-established value (e.g. cross-check against a shop the app already has an active session/webhook subscription for) before constructing `WebhookMetadata`.
- At minimum, document that `WebhookMetadata.shop` is NOT authenticated by `Utils::HmacValidator.validate` and must not be trusted as tenant-authoritative without additional application-level verification.

### Proof of Concept
1. App merchant A (attacker) installs the vulnerable app on `attacker-shop.myshopify.com`. Shopify sends a legitimately HMAC-signed webhook (e.g. `app/uninstalled`) to the app's endpoint with headers:
   ```
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid HMAC over raw_body, computed with the app's shared client_secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   ```
   using body `raw_body = "{}"` (mirroring `test/webhooks/registry_test.rb` fixtures, e.g. `test_process_hmac_validation_fails` / the earlier registry test with `hmac = OpenSSL::HMAC.digest(...secret..., "{}")`).
2. Attacker captures this valid `(raw_body, x-shopify-hmac-sha256)` pair.
3. Attacker replays the exact same `raw_body` to the app's webhook endpoint but changes only the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, `HmacValidator.validate` succeeds because it only checks `to_signable_string` (`raw_body`), unchanged from the original signed request: [2](#0-1) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though the signature was never computed over that value: [4](#0-3) 
6. The app's handler performs tenant-scoped actions (e.g. data deletion/deauthorization logic for `app/uninstalled`) against `victim-shop.myshopify.com`, despite the event never actually originating from that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
