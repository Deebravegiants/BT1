## Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never part of the signed material. `ShopifyAPI::Webhooks::Registry.process` validates only the body-derived HMAC and then trusts `request.shop` as the tenant identity handed to the application's webhook handler. This breaks the intended identity binding: `shop_that_authenticated(body) == shop_attributed_to(handler)`.

### Finding Description
The signable string used for HMAC verification is defined as: [1](#0-0) 

and `shop` is read independently from an unauthenticated header: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e., the raw body) and compares it to the `hmac` accessor, never touching `shop`: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (the unauthenticated header value) to the application handler as the tenant identity for the delivered payload: [4](#0-3) 

Because the shop-domain header is excluded from the signed bytes, any party who has captured one legitimately-signed webhook body+HMAC pair (for example, from their own store/installation of the app — an unprivileged, self-service action) can replay that exact body and HMAC while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to claim the payload originated from a different, victim shop. `HmacValidator.validate` still returns `true` because the body/HMAC pair is untouched, and `Registry.process` will dispatch the handler with `shop: <victim-shop>` even though the body content actually belongs to the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity confusion: the app backend is made to believe a payload came from shop B when it actually came from shop A, without needing knowledge of `api_secret_key`, a leaked token, or TLS interception — only possession of one legitimately-delivered webhook (trivially obtainable by any merchant using the app on their own store). Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., to select which merchant's install/session/local DB row to update, to trigger business logic scoped to a tenant, or to log/attribute events), this can lead to cross-tenant data corruption or spoofed events being attributed to an unrelated merchant, which maps to the "cross-tenant access" class of Critical impact.

### Likelihood Explanation
Likelihood is limited by the practical bottleneck that an attacker still needs to intercept/capture their own valid webhook body+HMAC (e.g., by installing the app themselves, or sniffing their own delivery) and be able to make an HTTP call to the app's webhook endpoint with a substituted header — both are within reach of an ordinary, unprivileged app user with no special access, hence a realistic though not fully "point-and-click" exploitation path.

### Recommendation
Include the tenant-identifying header(s) (`shop-domain`, and ideally `topic`/`webhook_id`) in the HMAC-signable material, or independently verify that `request.shop` matches an already-known/authorized installation (e.g., cross-check against a stored session for that shop) before dispatching to the handler, rather than trusting the raw header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and a valid `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` using the app's real secret).
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` and `Utils::HmacValidator.validate` only check `B` against `H`, which still matches — validation succeeds.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it belongs to `victim.myshopify.com`.

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
