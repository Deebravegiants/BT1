Confirmed: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) validates only `Utils::HmacValidator.validate(request)`, and `HmacValidator.validate` computes the HMAC over `request.to_signable_string`, which for `Webhooks::Request` is defined as `@raw_body` only (`lib/shopify_api/webhooks/request.rb:36-38`). The `shop`, `topic`, `api_version`, and `webhook_id` fields are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`) and are never included in the signed data. `Registry.process` then forwards `request.shop` directly into `WebhookMetadata` for the handler to use as the tenant identity (`lib/shopify_api/webhooks/registry.rb:198-199`), so the "shop that produced a validly-HMAC'd body" and the "shop the handler is told to act on" are not the same authenticated value.

### Title
Webhook tenant identity (`shop`) is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts any request whose raw body produces a valid HMAC under the app's `api_secret_key`, but the `shop-domain` header that identifies which merchant/tenant the webhook belongs to is never part of the signed content.

### Finding Description
The HMAC signature is computed only over `to_signable_string`, which for `Webhooks::Request` returns `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values are pulled from HTTP headers with no cryptographic binding to the signed body [2](#0-1) . `HmacValidator.validate` only checks the digest over that signable string against the secret [3](#0-2) . `Registry.process` raises only if the HMAC check fails, then hands `request.shop` — an unauthenticated header value — to the handler as the tenant identity [4](#0-3) .

Because the same app `api_secret_key` is shared across every shop that installs the app, any merchant who legitimately installs the app on their own store receives real, validly-HMAC'd webhook deliveries for their own shop. Since the signature is scoped only to the body, an attacker (an ordinary, unprivileged installer of the target app) can capture a `(raw_body, hmac)` pair genuinely issued for their own store, then replay it against the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. The signature will still validate, because it is oblivious to the `shop` field, and the handler will process data as if it originated from the victim tenant — breaking the identity binding `authenticated_shop == shop_acted_on`.

### Impact Explanation
This crosses a tenant boundary: an attacker with no special privileges (just merchant access to their own trial/free store using the same app) can spoof the shop-of-origin for webhook payloads whose body content they control or can obtain from their own shop, causing the app to process/store data under a victim's tenant/session key. This matches the High-severity "cross-tenant access" class in scope, directly analogous to the auth-collision bug class where an unvalidated field is trusted for identity purposes despite not being covered by the cryptographic check.

### Likelihood Explanation
Any developer/merchant can install a public app to obtain valid `(body, hmac)` pairs signed with the app's shared secret, then simply resend the request with a different `shop-domain` header value — no secret material or privileged access is required beyond ordinary app installation. `Registry.process` performs no comparison of `request.shop` against any authenticated value, and no test in the suite validates that a mismatched shop should be rejected (`test/webhooks/registry_test.rb` tests only that the header value is passed through faithfully).

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signed content that is verified — or otherwise cryptographically bind the shop domain to the body — before trusting `request.shop` as tenant identity in `Registry.process`/`WebhookMetadata`. At minimum, cross-check `request.shop` against a shop known to be legitimately associated with the current install/session before acting on the payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of body>`, and some `raw_body`.
3. Attacker captures `raw_body` and its valid `hmac` value.
4. Attacker resends a POST to the same webhook endpoint with the same `raw_body`/`hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds because it only checks `raw_body` against the secret [5](#0-4) , and the handler executes with `shop: "victim-shop.myshopify.com"` [6](#0-5) .

### Citations

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
