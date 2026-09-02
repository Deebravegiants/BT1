### Title
Webhook HMAC signature only covers the request body, not the `shop-domain` header, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the trusted `shop` identity for a webhook exclusively from an HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`), while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. Because the shop identity is never part of the signed bytes, an attacker who possesses any single validly-signed webhook payload (trivially obtainable by installing the target public/multi-tenant app on their own free dev store) can replay that payload to the app's webhook endpoint after swapping the `shop-domain` header to point at a victim shop. The signature still validates, and `Registry.process` hands the handler a `WebhookMetadata` object asserting the victim's shop, breaking the tenant boundary.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, deliberately excluding all headers: [1](#0-0) 

The `shop` accessor, however, is read straight from an attacker-controlled header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes the expected signature purely from `to_signable_string` (the body) and compares it to the `hmac` header — it never incorporates `shop`, `topic`, or any other header into the signed material: [3](#0-2) 

`Webhooks::Registry.process` trusts this unauthenticated `shop` value directly when dispatching to the app's handler: [4](#0-3) 

The equality that should hold is:
`bytes verified by HMAC (== raw_body) == bytes used to derive tenant identity (== shop header)`
This equality is false — the gem verifies the body but acts on an independent, unverified header field. Since a single Shopify app uses one shared `client_secret` (and thus one HMAC key) across every shop that installs it, any shop owner who has installed the app — an unprivileged action available to any internet user — receives real webhooks correctly signed with the app's shared secret. That signed payload can be replayed with the `shop-domain` header rewritten to any other shop the app also has installed, and it will pass `HmacValidator.validate` unchanged.

### Impact Explanation
This is a cross-tenant data/identity confusion: the app's webhook handler will process the (attacker-controlled) body while believing it originates from the victim's shop (`data.shop` in `WebhookMetadata`). Depending on how the host app's handler uses `shop` (e.g., to look up the merchant's session/access token, update per-shop records, or trigger shop-scoped side effects), this can let an attacker inject data attributed to, or targeting, a shop they do not own — a cross-tenant access primitive matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is High/practical: obtaining one legitimate signed webhook only requires installing the same public app on an attacker-owned free/dev store (no privileged credentials, no `api_secret_key` needed by the attacker), then replaying it to the app's public webhook endpoint with the `shop-domain` header altered. No secrets are required to forge the header; the HMAC never covered it.

### Recommendation
Include the shop domain (and topic) in the signed/verified material, or otherwise bind the request's claimed shop to the signature — e.g., have `to_signable_string` incorporate the `shop-domain` and `topic` headers, or independently verify that the resolved shop corresponds to session/installation records via a channel that Shopify itself authenticates (not merely echoed headers), before invoking application handlers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`; a real webhook (e.g. `orders/create`) is delivered with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid signature over raw body>`.
2. Attacker captures this raw body + signature (body is unrelated to shop identity and can be attacker-chosen data since it's their own store).
3. Attacker resends the identical body and HMAC header to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only — matches — validation passes. [5](#0-4) 
5. `Registry.process` invokes the handler with `shop: "victim.myshopify.com"`, `body:` attacker-controlled data, despite the request never being signed by/for the victim shop. [6](#0-5)

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
