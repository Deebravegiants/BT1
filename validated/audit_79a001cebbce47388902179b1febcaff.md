### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted as the tenant identity but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then unconditionally trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers when dispatching to the app's handler. Because those header values are never included in the HMAC-signed content, the binding `shop (HMAC-authenticated) == shop (attributed to the delivered data)` does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read directly from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it with the `hmac` header: [3](#0-2) 

`Registry.process` uses this single check as the sole authentication gate, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` (unauthenticated header values) to build the object handed to the app's webhook handler: [4](#0-3) 

Because the app's `client_secret` (used to compute the webhook HMAC) is shared across every shop that installs the app, and only the raw body is bound to the signature, any party who can obtain one validly-signed webhook body/HMAC pair (e.g., by installing the app on their own store and receiving one of their own webhooks) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers with values belonging to a different (victim) shop. The HMAC check still passes because it only verifies that the body bytes were signed with the app's secret — it says nothing about which shop, topic, or webhook the body is legitimately associated with. The equality that the report's bug class flags is broken here: **`shop` value verified by HMAC (none) != `shop` value acted upon by the handler (header-derived)**.

### Impact Explanation
This allows cross-tenant confusion at the application layer: an attacker with a legitimate installation on any shop can cause the app's webhook handler to process arbitrary attacker-chosen body content while it is attributed to a different, victim shop. Any app logic that keys persistence, side effects, or authorization decisions by the `shop` (or `topic`/`webhook_id`) field of `WebhookMetadata` — which is the officially documented, expected pattern for consuming this gem's webhook API — inherits a cross-tenant data/state confusion vulnerability, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires that the attacker be able to install the target app on a shop they control (a standard, unprivileged capability for any Shopify merchant/developer) in order to obtain one legitimately-signed webhook body/HMAC pair, and the ability to send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `api_secret_key`, or other privileged credential is required.

### Recommendation
Bind the header-derived `shop`, `topic`, and `webhook_id` values into the HMAC-verified material (or otherwise cryptographically bind them to the signed body), or require the consuming application to independently validate that the header `shop` is one it has an active, expected subscription/session for before trusting it. At minimum, document prominently that `Registry.process`'s HMAC check only authenticates the body bytes and does not authenticate the `shop`/`topic`/`webhook_id` header values, so consuming apps must not treat `WebhookMetadata#shop` as an authenticated tenant identifier without additional verification (e.g., cross-checking against a known/installed shop list via `ShopValidator`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. for `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker crafts a new HTTP POST to the same app webhook endpoint using the identical body `B` and identical `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` (`B`) — validation succeeds since `B` and `H` are unchanged. [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process attacker-controlled data as though it originated from the victim shop. [6](#0-5)

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
