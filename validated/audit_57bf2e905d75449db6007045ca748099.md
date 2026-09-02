## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler come from unauthenticated HTTP headers. Because these header-derived identity fields are never bound to the HMAC, an attacker who obtains one valid `(raw_body, hmac)` pair for a webhook they control can replay it with a forged `x-shopify-shop-domain` header, causing the receiving app to process the payload as if it belonged to a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
It returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read straight from request headers, entirely outside the signed data: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which — per its generic contract — only checks that `compute_signature(verifiable_query.to_signable_string, secret) == received_hmac`: [3](#0-2) [4](#0-3) 

Since `to_signable_string` only covers `raw_body`, the HMAC check validates that the body bytes are authentic for *some* topic/shop that the app's secret was used to sign, but it does **not** bind that signature to the specific `shop` (or `topic`/`webhook_id`) claimed in the headers. `Registry.process` then constructs `WebhookMetadata` directly from these unauthenticated header values and passes it to the app's handler: [5](#0-4) 

The broken binding, as an equality that should hold but doesn't:
`hmac == HMAC(secret, raw_body || shop || topic)` is expected, but the gem only enforces `hmac == HMAC(secret, raw_body)`, leaving `shop` (the tenant identity handed to the app) unauthenticated.

This is the same bug class as the referenced report (`WeirollWallet.forfeit()` acting on state without checking the field meant to gate it): here, the gem hands a `shop` value to the app's tenant-scoped handler logic without that value ever having been checked against the cryptographic signature meant to authenticate the request's identity.

### Impact Explanation
Any attacker who can obtain one legitimate webhook delivery for a shop they control (trivial — e.g., install the app on their own dev store and trigger `orders/create` or any subscribed topic) can capture the exact `raw_body` + `x-shopify-hmac-sha256` pair. They can then replay this exact body/HMAC pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`webhook-id`) with a victim shop's domain. `HmacValidator.validate` still passes because it only checks the (unchanged) body against the (unchanged) HMAC — it never inspects the shop header. The app's `WebhookHandler#handle` then receives `WebhookMetadata` claiming to be from the victim shop, potentially causing the host application to write attacker-controlled webhook data into the victim tenant's records, trigger victim-scoped side effects (e.g., order fulfillment, GDPR data-request handling, app-uninstall cleanup) under a false shop identity — i.e., cross-tenant access/data corruption using only the attacker's own legitimately-signed traffic.

### Likelihood Explanation
Exploitation requires no secrets beyond what any merchant who installs the app already has: a dev/test store with the app installed to legitimately receive one signed webhook. Capturing that request and replaying it with a modified header is straightforward. The likelihood is bounded only by whether the host application's webhook handler trusts `WebhookMetadata.shop` for tenant-scoped actions (which is the gem's documented usage pattern), so this is realistically reachable through the gem's public `Webhooks::Request` / `Registry.process` API.

### Recommendation
Include the identity-relevant header fields (`shop`, `topic`, and ideally `webhook_id`) in the signed/verifiable representation, or otherwise cryptographically bind them to the payload before trusting them, e.g.:
```ruby
def to_signable_string
  "#{shop}|#{topic}|#{@raw_body}"
end
```
This requires Shopify's outgoing webhook signature to also cover these fields (Shopify does sign only the body today), so an alternative in-gem mitigation is to have `Registry.process` cross-check the header `shop`/`topic` against the shop/topic embedded in the verified JSON body content itself (where Shopify embeds shop-identifying data), rejecting webhooks where the header claims disagree with the signed body's own tenant/topic markers, before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the POST body `raw_body` and header `x-shopify-hmac-sha256` computed by Shopify with the app's real secret.
2. Attacker replays the exact same request to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes `HMAC(secret, raw_body)` — unchanged — and passes: [6](#0-5) 
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` and forwarded to the app's handler, which processes attacker-controlled `raw_body` content under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
