### Title
Webhook shop-domain identity spoofing — HMAC covers only the raw body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is never included in the HMAC signature computation. `Registry.process` validates the request's HMAC and then unconditionally hands `request.shop` to the host application's handler as the authenticated tenant, even though the signature never bound that value.

### Finding Description
`Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`Request#shop` is read straight out of the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely independent of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it against the `hmac` header — it never touches `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` performs exactly that HMAC check and then immediately dispatches to the handler using the unauthenticated `request.shop` value, with no comparison against any known/expected shop: [4](#0-3) 

The equality this breaks is: `shop authenticated by the HMAC` ≠ `shop delivered to the handler as the tenant key`. The secret (`Context.api_secret_key`) used to compute the HMAC is the app's single `client_secret`, shared across every shop that has installed the app — it is not shop-specific. Consequently, any legitimate, previously-observed valid `(raw_body, hmac)` pair (from a webhook the attacker's own shop received, or any publicly-observable webhook delivery) remains cryptographically valid no matter what `shop-domain` header value is attached to the replayed request, because the header is outside the signed material.

### Impact Explanation
An attacker who controls one shop installation of a multi-tenant app can capture a legitimate webhook delivery (raw body + valid `hmac-sha256`) sent to their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept the signature as valid (since the body/HMAC pair is genuinely correct for the shared secret) and pass `WebhookMetadata` with the attacker-chosen `shop` to the handler. If the host application uses `data.shop` as the tenant key to write/update records (a common pattern, e.g. "upsert order for shop X"), this results in cross-tenant data corruption/injection — the classic impact category of cross-tenant access via an identity value that is asserted but never cryptographically bound.

### Likelihood Explanation
Exploitability requires the attacker to have their own legitimate install of the app (to observe at least one valid body/HMAC pair) and knowledge/guessability of the victim's shop domain (`*.myshopify.com`, often discoverable). No access to `api_secret_key`, tokens, or TLS interception is required — only observation of traffic to an endpoint the attacker already legitimately controls. This is a realistic, unprivileged-attacker scenario matching the report's bug class (a value acted upon by the code but not covered by the cryptographic guarantee that is supposed to authenticate it).

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signed material, or independently verify that `request.shop` corresponds to a shop the app has an active session/installation for before dispatching to handlers — analogous to the Chainlink recommendation of validating the bound value's provenance instead of trusting it implicitly. At minimum, `WebhookMetadata`/`Registry.process` should require the host app to cross-check `data.shop` against its own tenant registry rather than treating the header as authenticated by the signature.

### Proof of Concept
1. App shop `attacker.myshopify.com` installs the vulnerable host app; Shopify delivers a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B` under the app's shared `client_secret`), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)` from their own traffic.
3. Attacker POSTs to the app's webhook endpoint with body `B`, `x-shopify-hmac-sha256: H` (unchanged, still valid since HMAC only covers `B`), but `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `HmacValidator.validate` passes (only checks `B` vs `H`) per [5](#0-4) .
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop = "victim.myshopify.com"` per [6](#0-5) , even though nothing in the signed payload ever named that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-31)
```ruby
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
