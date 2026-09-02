This confirms the vulnerability: the webhook HMAC signature covers only `@raw_body` (the request body bytes), while the `shop` value that gets bound into `WebhookMetadata` and handed to the app's handler is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, with no cryptographic tie between the two.### Title
Webhook `shop` identity is taken from an unauthenticated HTTP header while only the raw body is HMAC-verified - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by HMAC-checking only the raw request body, then builds `WebhookMetadata` using a `shop` value read straight from an HTTP header that is not covered by that signature. Any caller who can produce a validly-signed body (e.g., the operator of their own store, which legitimately receives HMAC-signed webhooks for their own shop) can replay that body while forging the `shop-domain` header to any other shop domain, and the host app's webhook handler will process/attribute the request to the forged shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhook requests this method is: [1](#0-0) 
i.e. only `@raw_body` is signed — the HMAC never covers any request header.

The `shop` identity used downstream, however, comes exclusively from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates the HMAC (against the body only) and then immediately trusts `request.shop` (the header) to construct the metadata handed to the app's handler: [3](#0-2) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop bound by HMAC signature` ≠ `shop delivered to WebhookHandler.handle`

Before the attack: a legitimate webhook for shop A arrives with body B, `hmac-sha256` header computed by Shopify over B using the app's `client_secret`, and `shop-domain` header = A. `HmacValidator.validate` succeeds because it only checks B against the hmac header; `request.shop` returns A.

After the attacker's request: the attacker (who owns/controls shop A and therefore legitimately receives real, validly-HMAC-signed webhooks for shop A) resends the exact same body B and hmac header, but substitutes `shop-domain: B (victim shop)`. `HmacValidator.validate(request)` still succeeds, because signature verification only ever touches `@raw_body`, which is unchanged and still matches the (unchanged) hmac. `Registry.process` then calls the app's handler with `WebhookMetadata.new(..., shop: request.shop, ...)` where `request.shop` is now the forged victim domain — the gem hands the host application a `shop` value that was never authenticated by the signature at all.

### Impact Explanation
This lets an attacker who legitimately controls one shop (and thus a stream of validly-signed webhooks for it) cause any app built on this gem to process webhook payloads under the identity of an arbitrary other shop domain. Because most Shopify apps use the webhook's `shop` field to select which merchant record/session/access-token context to update (e.g., app-uninstalled cleanup, order/customer data writes, GDPR redact handlers), this is a cross-tenant data confusion/cross-tenant access primitive rooted entirely in this gem's `Webhooks::Request`/`Registry` code, not in host-app misuse — the gem itself exposes `shop` as if it were verified when it is not.

### Likelihood Explanation
High. No secrets are required beyond what any merchant/app-installer already possesses (their own valid signed webhook traffic). The only requirement is the ability to send an HTTP request to the app's webhook endpoint with attacker-controlled headers and the previously-observed valid `(body, hmac)` pair — something trivially available to anyone who has installed the app on their own store and can capture one legitimate webhook delivery.

### Recommendation
Include the shop domain (and ideally topic/api-version) inside the HMAC-signed material, or otherwise cryptographically bind `shop-domain` to the signed body before trusting it — e.g., verify the signature over a canonical string that incorporates the header values Shopify also signs, or cross-check the header-provided shop against a value independently obtained from a source verified by the signature (such as validating the webhook against a known/expected shop from session storage rather than blindly trusting the header). At minimum, `Webhooks::Registry.process` and `Webhooks::Request` should not expose `shop` to `WebhookMetadata` without it being covered by `to_signable_string`/`HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and captures one legitimate webhook delivery: raw body `B`, header `X-Shopify-Hmac-Sha256: H`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `to_signable_string` returns `B` unchanged.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` and compares to `H` — succeeds, since neither changed. [4](#0-3) 
5. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))`, i.e. the app processes/attributes the webhook payload to `victim-shop.myshopify.com` even though that shop never sent or authorized it. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
