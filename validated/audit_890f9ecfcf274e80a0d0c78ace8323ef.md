## Title
Webhook `shop` domain header is not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` is computed **only** over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` headers are never included in the signed content, so any attacker who possesses one valid `(body, hmac)` pair for the shared app secret can attach an arbitrary `x-shopify-shop-domain` value and have it accepted as authentic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` / `validate_signature` compute and compare the signature strictly against `verifiable_query.to_signable_string`, i.e. the body — never the shop domain: [2](#0-1) 

`Request#shop` simply reads the unsigned header: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` (the header value) as the tenant identity passed to the handler, with no additional binding check: [4](#0-3) 

This is exactly the "field acted on but not covered by the HMAC" pattern: the equality the gem implicitly relies on is `hmac == HMAC(secret, body)` implying `shop == authentic_shop`, but the actual binding only guarantees `hmac == HMAC(secret, body)`; `shop` is fully independent and attacker-controlled.

### Impact Explanation
All shops that install the same app share one `client_secret`/`api_secret_key`, since HMAC validation only checks the shared app secret and not a per-shop key. Any merchant (an unprivileged multi-tenant actor from the app's perspective) that receives a genuine webhook from Shopify for their own shop obtains a valid `(body, hmac)` pair. They can replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because the signable string (body only) is unchanged, and `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the forged victim domain. Any app logic that trusts `data.shop` to select the tenant record/session to act on (a very common pattern for webhook handlers) will process attacker-supplied data under another merchant's identity — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate merchant who has installed the target app (no special privilege), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both trivially available to any external, unprivileged actor. No secrets, tokens, or elevated access are required.

### Recommendation
Bind the shop identity (and ideally topic/webhook id) into the value that is cryptographically verified, e.g. include `shop-domain` in the signable string, or independently verify that the shop in the header matches the shop associated with an app-tracked webhook subscription/session before dispatching to handlers, rather than trusting the raw header value once only the body's HMAC has been checked.

### Proof of Concept
1. App is installed on both `attacker.myshopify.com` and `victim.myshopify.com` (same app, same `client_secret`).
2. Shopify sends a genuine webhook to the app for `attacker.myshopify.com`:
   - body: `{"id": 1, ...}`
   - header `x-shopify-hmac-sha256: H` (valid HMAC of body under the shared secret)
   - header `x-shopify-shop-domain: attacker.myshopify.com`
3. Attacker captures this exact `(body, H)` pair (e.g., by controlling the receiving proxy for their own shop, or from their own server logs if they self-host a relay) and re-POSTs it to the app's webhook route, replacing only the header:
   - header `x-shopify-shop-domain: victim.myshopify.com`
   - body and `x-shopify-hmac-sha256` unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over the unchanged body and it matches `H` — validation succeeds.
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)`, causing the app to act on the victim tenant using attacker-supplied content.

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
