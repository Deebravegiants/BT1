### Title
Webhook `shop` (and `topic`) identity is trusted from an HTTP header that is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC over the request body, but then trusts the `shop` (and `topic`) values taken from HTTP headers that are **not** included in the HMAC-signed bytes. Any party who can obtain one legitimately-signed webhook (e.g. by installing the app on their own store) can replay that exact signed body while forging the `X-Shopify-Shop-Domain` header to name a different, victim shop. The signature still validates, because the signable string is only the raw body.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable content as only the raw body: [1](#0-0) 

But `shop` (and `topic`) are pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is attacker-controlled and never mixed into `to_signable_string`: [2](#0-1) 

`Registry.process` (the gem's documented entry point for handling an incoming webhook) validates the HMAC over the request and, once it passes, immediately trusts `request.shop` and `request.topic` as the tenant/event identity handed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
```
bytes covered by HMAC == bytes the app trusts to identify the shop
```
Here, `bytes covered by HMAC == @raw_body` while `bytes the app trusts to identify the shop == headers["shop-domain"]`, which is a strictly larger, unauthenticated surface. Because the header is outside the signed payload, an attacker can take one authentic `(raw_body, hmac)` pair — trivially obtainable by installing the app on any store they control, since Shopify sends real webhooks with a valid HMAC computed with the app's `client_secret` for every shop that installs the app — and resubmit it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` will succeed because it only recomputes the signature over `raw_body`: [4](#0-3) 

The handler then receives `WebhookMetadata` with `shop:` set to the attacker-chosen victim domain, even though the body content originates from the attacker's own store.

### Impact Explanation
This is a cross-tenant identity break: the gem hands the host application a `shop` value that it advertises as an authenticated, HMAC-verified field, but that field can be freely forged by anyone who has ever received one real webhook for any shop (including their own). Host applications built against this gem's documented `WebhookMetadata.shop` contract (the very reason the field exists) will process webhook payloads under the wrong tenant's identity — e.g. writing attacker-controlled data into a victim shop's records, or triggering shop-scoped side effects (such as `shop/redact`, `customers/redact`) against a shop the attacker does not control. This matches the "cross-tenant access" Critical-impact bucket.

### Likelihood Explanation
The only prerequisite is the ability to install the target app once on an attacker-controlled store (a routine, unprivileged action for any Shopify merchant/developer) to obtain one real `(raw_body, hmac)` pair, then replaying it to the app's public webhook endpoint with a rewritten `shop-domain` header. No access to the app's `client_secret`, no TLS interception, and no privileged account are required — only ordinary interaction with the app as an unprivileged merchant.

### Recommendation
Bind the `shop` (and `topic`) claim to the HMAC-verified content instead of trusting a raw header. Options:
- Extend `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to include the `shop-domain` and `topic` header values so that any tampering invalidates the signature.
- Alternatively, cross-check the header-derived `shop` against an independently-authenticated source (e.g. the shop associated with the webhook subscription being looked up) before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. Install the target app on an attacker-owned development store; capture a real webhook delivery (e.g. `orders/create`), noting the raw body and the `X-Shopify-Hmac-Sha256` header value.
2. Replay the exact same HTTP request to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` returns `true` because the signature only covers `@raw_body`, which is unchanged.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, so the host application processes attacker-controlled data as if it originated from the victim shop. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
