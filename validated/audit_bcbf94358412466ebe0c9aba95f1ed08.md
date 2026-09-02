### Title
Webhook HMAC only signs the request body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the shop identity that the SDK hands to the app's webhook handler (`data.shop`) is read from the unauthenticated `x-shopify-shop-domain` header. Because the same `client_secret` HMAC key is shared across every shop that installs a given app, any user who can obtain one valid `(body, hmac)` pair for *their own* shop can replay it to the app's webhook endpoint with a forged `shop-domain` header pointing at a *different* shop, and the signature will still validate — breaking the binding between "HMAC-authenticated bytes" and "the shop the webhook is attributed to."

### Finding Description
`ShopifyAPI::Webhooks::Request` is the object the host application feeds into `ShopifyAPI::Webhooks::Registry.process`: [1](#0-0) 

Its `to_signable_string` (used by `HmacValidator`) returns `@raw_body` only: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then dispatches the handler using the unauthenticated `shop` header as the tenant identifier: [4](#0-3) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e. the body, using the app's single, cross-tenant `Context.api_secret_key`: [5](#0-4) 

The identity binding that should hold is:
`shop header value == shop that produced the HMAC-signed bytes`

Before the attack: Shopify sends webhook `(body_A, hmac(body_A), shop-domain: A)` to the app for tenant A only.

After the attack: an installer of the app on shop A (an "unprivileged" user with respect to any other tenant of the same app) captures their own legitimate `(body_A, hmac(body_A))` pair (trivial — they own shop A and can see their own webhook deliveries/logs, or simply issue an event on their own store) and replays it directly to the app's public webhook endpoint with `x-shopify-shop-domain: B.myshopify.com`. `HmacValidator.validate` recomputes `HMAC(secret, body_A)`, which still matches, because the shop header was never part of the signed material. `Registry.process` then calls the handler with `WebhookMetadata.new(topic: ..., shop: "B.myshopify.com", body: parsed body_A, ...)` — the app now believes tenant B produced this event/data.

### Impact Explanation
This is a cross-tenant access primitive: a party with no relationship to shop B (only their own shop A, in an app installed by both) can inject events/data that the host application will process and attribute to shop B under a validly-verified HMAC. Depending on what the app does in its webhook handler (e.g., updating stored order/customer/inventory data keyed by `shop`, triggering emails, changing app-level state for that tenant), this can lead to data corruption, business-logic manipulation, or information disclosure across tenant boundaries — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Any legitimate app installer already possesses a working `(body, hmac)` pair for their own shop simply by using the app normally (webhooks fire on ordinary events). No secrets, tokens, or privileged access are required to obtain the forged pair or to send the crafted HTTP request to the app's public webhook endpoint. The only requirement is that the same app is installed on both the attacker's shop and the victim's shop, which is normal in a multi-tenant SaaS app — a very low bar.

### Recommendation
Include the header-derived, security-relevant fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) as part of the HMAC-signed material (or otherwise cryptographically bind them, e.g. only accept `shop` values matching sessions the app has an active install for and cross-check topic against message content), so that changing any of these headers invalidates the HMAC, matching Shopify's own webhook verification guidance which signs the request but assumes the header trio is delivered over the same trusted channel as the body — at minimum, `Registry.process` should refuse to trust the `shop` header unless it corresponds to a shop the app currently has a stored session/install for.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers or observes any real webhook Shopify sends to the app, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value (their own legitimate webhook, so this is trivially obtainable).
3. Attacker POSTs the same `raw_body`/`X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `raw_body`; `HmacValidator.validate` recomputes the same HMAC using the app's shared `client_secret` and it matches. [6](#0-5) 
5. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker's body, even though the data never came from `victim.myshopify.com`.

### Citations

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
