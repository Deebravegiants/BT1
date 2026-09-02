## Analog Finding

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing shop/tenant spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported bug's root cause is that `withdrawToken()` acted on a `tokenId` that was not properly bound to the caller's authorized withdrawal amount, letting an unprivileged caller detach state that should only change atomically with a validated action. The analogous binding break in this gem is that `ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the `shop-domain` header that downstream handlers rely on as the tenant identity is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against this signable string: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` treats a passing HMAC check as authorization to trust every other field parsed off the request, including `shop`, and forwards it straight to the app's handler as the tenant identity: [3](#0-2) 

`request.shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cross-check against the signed body: [4](#0-3) 

The binding that should hold is:

`hmac_signed_bytes == bytes_the_gem_uses_to_derive_tenant_identity`

but in reality:

`hmac_signed_bytes = raw_body` while `tenant_identity = header["shop-domain"]`

Any unprivileged user who can install the same app on their own shop (a normal, unprivileged action) receives real, correctly-HMAC'd webhooks from Shopify for their own shop. Because the `shop-domain` header sits outside the signed bytes, that attacker can replay the exact same body+HMAC pair to the app's webhook endpoint while substituting the victim shop's domain in the header. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` hands the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee: the gem asserts "this payload was authentically sent by Shopify for shop X," but shop X is attacker-controlled. Any host application that uses `WebhookMetadata#shop` (as documented) to determine which merchant record to update, without independently re-validating the shop against its own stored, authenticated session data, can have attacker data attributed to and processed against an arbitrary victim tenant — a cross-tenant confusion analogous to the "detach anything without full validation" pattern in the source report.

### Likelihood Explanation
Requires only that the attacker be a legitimate (unprivileged) merchant/installer of the same app — no `api_secret_key`, access token, or privileged access is needed. Capturing a legitimate webhook delivery (e.g., via their own store's webhook logs/inspector) and replaying it with a modified `shop-domain` header is straightforward and requires no cryptographic material.

### Recommendation
Include the authenticated shop identity in the signed material the library trusts, or explicitly document/enforce that consumers must independently verify `WebhookMetadata#shop` against a session/store they already trust before acting on the payload. At minimum, the gem should not present `shop` as if it were HMAC-verified when it is not.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared secret), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds.
4. `handler.handle` receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to act on attacker-supplied data under the victim's tenant identity.

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
