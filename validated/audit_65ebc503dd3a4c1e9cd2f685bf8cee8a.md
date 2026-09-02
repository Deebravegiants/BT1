### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as fully authenticated once `Utils::HmacValidator.validate` succeeds, then hands the handler a `WebhookMetadata` object built from `request.shop`. However, the HMAC only signs the raw request body — the `shop-domain` header used to identify the tenant is never included in the signed material. Any party who can obtain one valid `(body, hmac)` pair for the shared app secret (trivially available to any merchant who has installed the app and receives their own legitimate webhooks) can resubmit that exact body/HMAC pair to the app's webhook endpoint with an arbitrary `shop-domain` header, and the gem will report it as a validly-authenticated webhook "from" the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the (unauthenticated) header, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` only ever compares `verifiable_query.hmac` against an HMAC of `to_signable_string` (i.e., the body) — the `shop` field never enters this computation: [3](#0-2) 

`Registry.process` gates everything on that single HMAC check and then trusts `request.shop` as the tenant identity handed to the handler: [4](#0-3) 

The identity binding that should hold is:
`authenticated_source(body) == tenant_identity(shop_header)`

But the code only proves `signature_valid(body)`; it never proves `shop_header` was the shop the signature was produced for. Because the app's `api_secret_key` is a single secret shared across every shop that installs the app (not shop-specific), any merchant/tenant that legitimately receives one webhook (with a valid `body`+`hmac` pair for their own shop) can replay that exact pair against the app's public webhook endpoint while substituting a different `shop-domain` header. The gem will validate the HMAC (since it only checks the body) and dispatch the handler believing the data originated from the victim shop, even though the header claiming that shop was never covered by the signature. This is a direct instance of "a field acted on but not covered by the HMAC."

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce: `request.shop`/`WebhookMetadata#shop` is the field host applications use to look up per-tenant state (installed shop record, access token, business data) and act on it. An attacker who is merely one of the app's own installed merchants (unprivileged relative to other tenants) can forge a webhook that the gem certifies as validly signed for a *different* merchant's shop domain, injecting attacker-controlled body content under another tenant's identity. This is a cross-tenant access/confusion vulnerability at the credential/identity-binding layer that this gem is responsible for enforcing before ever calling into the handler.

### Likelihood Explanation
No secret material is required beyond what an ordinary (even low-trust) installed merchant already legitimately possesses — a single previously-received `(body, hmac)` pair from their own store's webhook traffic. Webhook endpoints are public HTTP(S) endpoints reachable by any internet client, and the replay requires nothing more than substituting one header value. No unique circumstances, race conditions, or elevated privileges are needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) values into the signed material that `HmacValidator` verifies, e.g., include the `X-Shopify-Shop-Domain` header (and other identity-bearing headers) in `Request#to_signable_string` so the tenant identity cannot be altered independently of a validly-signed body. At minimum, `Registry.process` should require that the tenant identity used for dispatch was itself part of the HMAC-verified content, not read from an out-of-band header.

### Proof of Concept
1. App merchant "Attacker" installs the app on `attacker-shop.myshopify.com` and legitimately receives a real webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, computed by Shopify with the app's shared `client_secret`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with:
   - Body: the same `B` (or any body reusing a previously captured valid `H` for a chosen body)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid for `B`)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged, arbitrary)
   - Header `X-Shopify-Topic: orders/create`
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate` succeeds because it only recomputes the HMAC over `@raw_body`, matching `H`: [4](#0-3) 
4. `Registry.process` invokes the app's registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, even though the HMAC never certified that this body belongs to `victim-shop.myshopify.com`. The host application, trusting the gem's "Invalid webhook HMAC" gate, now processes attacker-controlled data under the victim tenant's identity.

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
