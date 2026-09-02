## Title
Webhook shop identity spoofing via unauthenticated `X-Shopify-Shop-Domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (tenant identity) that gets handed to the app's webhook handler is read from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header, which is never included in the signed payload. An attacker who can obtain any single validly-signed webhook (e.g. by installing the app on their own store and receiving a real webhook from Shopify) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header value, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it to the app's handler tagged with the attacker-chosen shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the (attacker-controllable, at the HTTP layer) `shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` and forwards it to the app's handler as the tenant identity for the delivered payload: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature strictly against `to_signable_string`, i.e. the body only: [4](#0-3) 

This breaks the intended identity binding:
`HMAC-verified(body)` == `identity used by handler (shop header)`
should hold, but in fact `shop` is never covered by the HMAC, so:
`verified(raw_body)` ≠ `bytes that determine tenant (shop-domain header)`.

An unprivileged internet user can install the target app on their own (attacker-controlled) development/test shop, capture one legitimately-signed webhook delivery (any topic works, since `topic` is likewise unsigned and only used for handler dispatch), then replay that exact `(raw_body, hmac-sha256 header)` pair to the app's public webhook endpoint while swapping the `shop-domain` header to a victim shop's domain. `Registry.process` will pass the HMAC check (since the body/HMAC pair is genuinely valid) and call the app's handler with `WebhookMetadata.new(shop: "<victim-shop>", ...)`, injecting attacker-controlled body content attributed to another tenant.

### Impact Explanation
This crosses a tenant boundary: any code in the host application that uses `data.shop`/`WebhookMetadata#shop` to select the storage record, session, or access token to act on (a standard pattern for multi-tenant Shopify apps processing webhooks) can be made to apply attacker-supplied webhook content to a different shop's tenant context. This satisfies the Critical "cross-tenant access" impact category, since the gem itself asserts the payload came from `shop-domain` without cryptographically binding that claim to the verified bytes.

### Likelihood Explanation
Any internet user can create a Shopify development store, install an app that uses this gem, and receive at least one genuinely HMAC-signed webhook for their own store — no privileged credentials, leaked secrets, or access to the app's `client_secret` are required. Replaying that captured request with a forged `shop-domain` header is a simple, deterministic HTTP replay; the gem performs no additional binding check between the header and the signed body.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the material verified against the HMAC, or otherwise cryptographically bind the `shop-domain` header to the specific signed delivery, e.g. by requiring the host app look up the shop via a value derived from data inside the verified body/registration rather than trusting the raw header value for tenant selection. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used by itself to select a tenant/session.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with an empty or attacker-crafted body `B`.
2. Shopify delivers headers including `X-Shopify-Hmac-Sha256: H` (valid for secret `S` and body `B`) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the exact same body `B` and `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `B` against `H` [5](#0-4) 
5. `Registry.process` calls the registered handler with `shop: "victim.myshopify.com"` and the attacker's body content [6](#0-5) 
even though Shopify never generated any webhook for `victim.myshopify.com` with this content.

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
