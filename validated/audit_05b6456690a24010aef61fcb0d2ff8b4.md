## Finding

The Webhooks HMAC validation in this gem authenticates only the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values used by webhook handlers are taken from unauthenticated HTTP headers and are never included in the signed bytes.

### Title
Webhook `shop` (and other tenant-identifying headers) not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` by defining `to_signable_string` to return only `@raw_body` [1](#0-0) . However, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-suppliable HTTP headers [2](#0-1)  and none of these header values participate in the HMAC computation. `Registry.process` validates the request's HMAC and then dispatches the handler using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` taken directly from those same unauthenticated headers [3](#0-2) .

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the `hmac` value with `OpenSSL.secure_compare` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only the raw body [1](#0-0) , so the signature proves only "this body was signed with the app's `client_secret`" — it proves nothing about which shop, topic, or webhook id the caller claims.

Because `client_secret` (the webhook signing secret) is shared by the app across *all* installing shops (it is not per-tenant), any shop that has installed the app can obtain a legitimately-signed `(raw_body, hmac)` pair from its own real webhook deliveries. That pair remains valid regardless of what `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers accompany it, since those headers are never part of the signed bytes.

This breaks the intended binding:
```
shop authenticated by HMAC == shop the handler attributes the payload to
```
In reality: `shop authenticated by HMAC` is undefined (HMAC only binds the body), while `shop the handler attributes the payload to` = `request.shop`, an unauthenticated header value [5](#0-4) .

### Impact Explanation
An attacker who controls a shop that has installed the target app can capture a valid `(raw_body, hmac)` pair from one of their own real webhook deliveries (e.g., an `orders/create` payload), then replay that exact body/HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) to point at a victim shop. `Registry.process` will pass HMAC validation (the body is genuinely signed) and will invoke the app's handler with `WebhookMetadata` claiming the data belongs to the victim shop [6](#0-5) . Any app logic that trusts `data.shop` to scope database writes, billing actions, or downstream side effects per tenant can be tricked into cross-tenant data injection/corruption — this satisfies the "cross-tenant access" high/critical impact category.

### Likelihood Explanation
Likelihood is realistic for any app that: (1) allows public installs (so an attacker can become a legitimate installing "shop" and harvest real signed webhook bodies), and (2) exposes its webhook endpoint publicly, which is required for Shopify webhook delivery in the first place. No credentials beyond a free shop install are needed; `client_secret` itself is never exposed to the attacker.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signed material that `HmacValidator` checks for webhooks, or otherwise cryptographically bind them to the payload before dispatch (e.g., validate that the header-derived shop matches a shop-suffix embedded/signed in the body, or maintain a per-shop webhook secret if the API ever supports one). At minimum, document and enforce that consumers of `WebhookMetadata#shop`/`#topic` must not treat them as authenticated unless bound to the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and receives a real webhook, e.g. body `B` with header `shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(client_secret, B)`), and header `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs the exact same body `B` and header `shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally alters `shopify-topic`/`shopify-webhook-id`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) — this matches `H`, so validation passes [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
