## Title
Webhook `shop` (and topic/webhook-id/api-version) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the shop identity used to dispatch the webhook to app-side handlers comes from an unsigned HTTP header. An attacker who can obtain one legitimately-signed webhook (e.g., by triggering an event in their own connected shop) can replay it to the app's webhook endpoint with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header, and the signature will still validate — because that field was never part of the signed content.

## Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body, and `hmac`/`shop`/`topic`/`webhook_id`/`api_version` are all pulled straight from HTTP headers that are never part of the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then dispatches to the handler using `request.shop` (and other header-derived fields) without any additional binding to what was actually signed: [3](#0-2) 

This breaks the identity binding the rules call out: `hmac(raw_body)` verifies "bytes verified", but `shop` used to route/act on the webhook is "bytes parsed" from an unsigned header — i.e. `shop_used_for_dispatch != shop_covered_by_hmac`. Since Shopify's webhook HMAC secret (`api_secret_key`) is shared across every shop installed on a given app, any merchant (an "unprivileged" party with respect to other tenants of the same app) who receives one authentic webhook call can capture the `(raw_body, hmac)` pair and replay it against the same app's webhook endpoint while substituting a different shop's domain in the header. The signature check passes because it only re-derives the HMAC from the untouched body.

## Impact Explanation
This allows cross-tenant confusion: a handler that trusts `WebhookMetadata#shop` (built directly from `request.shop`) to look up per-shop session/config/state, or to attribute the payload's data to a shop, can be made to act on behalf of a shop the attacker does not own. Depending on how the host app's handler uses `data.shop` (e.g., loading that shop's offline access token to make further API calls, or writing/deleting data keyed by shop), this can enable cross-tenant access or data manipulation, matching the "cross-tenant access" impact tier.

## Likelihood Explanation
The prerequisite — causing (or already having) one valid webhook from any shop under the same app, plus the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a modified header — is realistic for any merchant/tenant of a multi-tenant app, since webhook endpoints are public HTTP(S) endpoints and headers are attacker-controlled outside of the signed body.

## Recommendation
Include the identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material, or otherwise cryptographically bind the header-derived `shop` to the request before it's handed to `WebhookMetadata`/handlers — e.g., verify the `shop` domain against the shop that is authorized/subscribed for that specific webhook subscription (server-side lookup) rather than trusting the header verbatim once the body-only HMAC passes.

## Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, using the same `api_secret_key`.
2. Shopify sends a legitimate webhook to the app for `shop-a`:
   - Headers: `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac of raw_body>`
   - Body: `{"id": 123, ...}`
3. Attacker (who controls/observes traffic to `shop-a`'s endpoint, e.g., is the `shop-a` merchant) captures `raw_body` and `hmac`.
4. Attacker resends the identical request to the app's webhook endpoint but changes only the header: `x-shopify-shop-domain: shop-b.myshopify.com`.
5. `HmacValidator.validate` in `Registry.process` recomputes the HMAC solely from `raw_body` [4](#0-3) , which is unchanged, so validation succeeds, and the handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the payload was never actually generated for `shop-b`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
