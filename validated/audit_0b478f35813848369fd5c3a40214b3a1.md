### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` validates the incoming HMAC solely against that raw body. However, the `shop` field extracted from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header is passed unchanged into the merchant-facing `WebhookMetadata` handed to the app's webhook handler, without that header ever being included in the signed payload.

### Finding Description
The identity binding that should hold is:

`hmac == HMAC(api_secret_key, raw_body)` **and** `shop (trusted identity used by handler) == shop (covered by hmac)`

In this gem, only the first half is true. `Request#to_signable_string` is defined as: [1](#0-0) 
which returns just `@raw_body`, never the `shop-domain` header. `Request#shop` simply reads the unauthenticated header value: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` to the app's handler as the trusted tenant identifier, with no check that this shop value is bound to the signature that was verified: [3](#0-2) 

Because all of a given app's webhooks — regardless of which merchant/shop they originate from — are signed with the same, single `api_secret_key` (the shop is not part of the keyed material or the signed string), the signature over the body proves only "this body was HMAC'd with my app's secret." It proves nothing about which shop the body is associated with. The `shop` field that the handler treats as the authenticated tenant identity is therefore never actually verified against the HMAC — it is trusted from the header alone.

### Impact Explanation
Any party able to submit a request (with a body/HMAC pair that is valid for the app's secret) to the app's webhook endpoint can freely set the `shop-domain` header to an arbitrary tenant's domain, and `Registry.process` will pass that spoofed shop straight into the handler as if it were verified. Applications built on this library that key persistence, authorization, or side effects (e.g., "update this shop's order/inventory record") off of `WebhookMetadata#shop` will attribute or apply webhook data to the wrong tenant — a cross-tenant identity confusion rooted entirely in this gem's own `Request`/`Registry` code, not in any misuse of undocumented behavior.

### Likelihood Explanation
Exploitation requires only the ability to reach the app's public webhook endpoint with a body whose HMAC matches the app's secret over that body — the shop identity itself carries no cryptographic binding, so no privileged credentials, leaked secrets, or social engineering are needed to forge the tenant association once a validly HMAC'd body/header pair (as delivered for one's own shop) is replayed with a modified `shop-domain` header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material checked by `HmacValidator`, or otherwise cryptographically bind the `shop-domain` header to the verified HMAC before exposing `WebhookMetadata#shop` to application handlers, so the trusted shop identity used downstream is provably the same shop whose signature was validated.

### Proof of Concept
1. Register the app's webhook handler as shown in `docs/usage/webhooks.md` (`ShopifyAPI::Webhooks::Registry.process`).
2. Obtain (as the operator of shop `attacker.myshopify.com`, a legitimately installed tenant) a real webhook delivery: raw body `B` and its valid `x-shopify-hmac-sha256` header `H`, both signed with the app's shared `api_secret_key`.
3. Replay the request to the app's webhook endpoint unchanged except for the `x-shopify-shop-domain` header, setting it to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `H` against `B` (see `to_signable_string` returning `@raw_body`).
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though nothing about `victim-shop.myshopify.com` was ever signed — demonstrating the shop identity is unauthenticated relative to the HMAC that gates processing.

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
