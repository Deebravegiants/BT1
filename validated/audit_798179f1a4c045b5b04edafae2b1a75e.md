### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC computed over the raw request body, then dispatches to the app's handler using the `shop` value taken from an HTTP header that is never included in that signature. The identity binding the app relies on — "the shop this payload is attributed to" — is not the same as "the shop covered by the HMAC," so an entity that can produce one genuine `(body, hmac)` pair for the shared app secret can re-attribute that payload to a different shop.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, and for webhooks that string is exactly `@raw_body`: [1](#0-0) 
The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely outside the signed material: [2](#0-1) 
`Registry.process` checks only `Utils::HmacValidator.validate(request)` and then immediately forwards `request.shop` to the app's handler as the authoritative tenant identifier: [3](#0-2) 

The equality the code assumes is:
`shop authenticated by the HMAC == shop used to route/attribute the webhook data`

But the HMAC only proves `body == HMAC_verify(raw_body, secret)`; it says nothing about which shop the header claims. Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any holder of one genuine `(raw_body, hmac)` pair — obtained from a webhook legitimately delivered for their own shop — can resubmit that exact body/HMAC pair to the app's webhook endpoint while substituting a different value in `x-shopify-shop-domain`. `HmacValidator.validate` will still pass because the body is unchanged, yet `WebhookMetadata.shop` will report the attacker-chosen shop to the handler.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an app that keys any per-tenant state (session lookup, data merge, `shop/redact`/`customers/redact` compliance actions, billing counters, etc.) off `WebhookMetadata#shop` can be made to apply data or trigger actions against a shop the attacker does not own — a cross-tenant integrity issue that maps directly to the "field acted on but not covered by the HMAC" identity-binding failure class.

### Likelihood Explanation
Exploitation requires only that the attacker have legitimately received one webhook delivery for their own installed shop (any topic works, since the HMAC never binds shop, topic, or webhook id) and network access to POST to the app's public webhook endpoint — no privileged credentials, access tokens, or `api_secret_key` knowledge are needed. This satisfies the "unprivileged internet user" bar.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header value into the signed material checked by `HmacValidator`, or otherwise cross-validate `request.shop` against a value derived from the body/HMAC before dispatching to handlers, so that the shop attribution cannot be altered independently of the signature.

### Proof of Concept
1. Install the app on shop A (attacker-controlled) and capture one real webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` passes because it only checks `B` against `H`; `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to act on/attribute data under the victim shop's identity.

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
