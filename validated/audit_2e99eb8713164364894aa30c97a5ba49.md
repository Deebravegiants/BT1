### Title
Webhook `shop-domain` header is not bound to the HMAC signature, allowing cross-tenant shop spoofing on webhook delivery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` (and `topic`, `api_version`, `webhook_id`) are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the *body* was HMAC-signed with the app's secret; it never proves that the `x-shopify-shop-domain` header the app subsequently trusts as the tenant identifier actually corresponds to the shop that produced that body/signature pair.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `shop` is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates the request using only this body-bound HMAC and then hands `request.shop` straight to the app's webhook handler as the trusted tenant identifier: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever checks `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC secret: [4](#0-3) 

The broken identity binding is: `HMAC(raw_body, api_secret_key) == received_hmac` is treated as proof that `shop-domain header == the shop that generated this event`, but the header is never part of the signed content. An attacker who legitimately controls one shop installation of the app will receive real webhook deliveries (valid body + valid HMAC, signed with the app's shared secret) for their own shop. They can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (it never inspected the header), so `Registry.process` invokes the handler with `shop: <victim shop>` and the attacker-controlled body content.

### Impact Explanation
This breaks the tenant boundary the gem's own webhook API contract implies: `WebhookMetadata#shop` is documented as the authenticated identity of the originating shop, when in fact it is unauthenticated attacker-controlled data as long as the attacker can produce *any* validly-signed body for the same app (trivial, since they own a shop with the app installed). Any host application that uses `request.shop` / `WebhookMetadata#shop` to select which tenant's data to update (the intended and expected use of this field) can be tricked into applying attacker-supplied webhook payloads to a different merchant's tenant/session — a cross-tenant data-integrity and confidentiality violation.

### Likelihood Explanation
Requires only an unprivileged attacker to install the target app on their own (attacker-controlled) shop — a normal, freely available action for any public Shopify app — to obtain one legitimately-HMAC-signed body/header pair, then replay it against the exposed webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the shop domain (and other trust-sensitive headers such as topic/api-version) into the signed material that is validated, or otherwise cryptographically tie the header set to the specific HMAC-verified request (e.g., derive/validate the shop identity from the session/access token used to fetch the resource, not solely from an unauthenticated header), matching how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop`/`host` in its signable content.

### Proof of Concept
1. Attacker installs the target Shopify app on shop `attacker.myshopify.com`.
2. Attacker triggers an event that causes the app to send them a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the same `B`/`H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B, api_secret_key) == H` — true — and proceeds to call `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...))`, feeding attacker-controlled body data under the victim's tenant identity.

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
