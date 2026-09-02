## Title
Webhook shop identity is not bound by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC only over the raw request body, while the `shop` (merchant tenant identity) is read from a separate, unsigned header. Because the HMAC secret (`api_secret_key`) is shared across every shop that installs the same app, any merchant who has installed the app can obtain a validly-signed webhook payload for their own store and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain`/`shopify-shop-domain` header swapped to a victim shop, and the signature will still validate. Handlers receive the attacker-controlled body attributed to the victim tenant, breaking the tenant isolation the HMAC check is supposed to guarantee.

### Finding Description
`Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)` and then dispatches to the handler using `request.shop` for tenant attribution: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value, both of which come from the `Request` object: [2](#0-1) 

Critically, `Webhooks::Request#to_signable_string` returns only the raw body — the `shop` field is *not* included in the signed content: [3](#0-2) [4](#0-3) 

Compare this with the OAuth callback path, `Auth::Oauth::AuthQuery#to_signable_string`, where `shop` *is* explicitly included in the signable content, so a forged `shop` value there is correctly rejected by the HMAC check: [5](#0-4) 

Since `api_secret_key` is the same secret for every shop that has the app installed (it is the app's client secret, not a per-shop secret), a signature computed for one shop's webhook body is equally valid for any other shop's webhook, as long as the body is unchanged. The `Request#shop` used for tenant attribution comes from a header that carries no cryptographic binding to the signed body: [6](#0-5) 

This breaks the intended identity binding: `hmac(body) == hmac(body)` holds, but the `shop` attribute forwarded to the handler is attacker-controlled rather than being the shop that legitimately produced the signed body.

### Impact Explanation
This is a cross-tenant identity binding failure: an app that trusts `WebhookMetadata#shop` (built directly from `request.shop`) to identify which merchant's data/event a webhook body belongs to can be made to process attacker-supplied JSON under another merchant's identity. Depending on how the host application uses the webhook `shop` field (e.g., looking up shop-scoped records, updating billing/state, or writing merchant-scoped data), this can lead to cross-tenant data corruption or unauthorized actions performed against a victim shop's tenant context — meeting the "cross-tenant access" bar for Critical impact.

### Likelihood Explanation
Exploitation only requires an attacker to be a legitimate merchant of the target app (a normal, unprivileged signup — no leaked secrets, no access token, no social engineering needed). The attacker triggers a real Shopify event on their own store to obtain a genuinely HMAC-signed payload for a body they control (e.g. an order/customer webhook with attacker-chosen fields), then POSTs that exact body/HMAC pair to the app's public webhook endpoint with the `shop-domain` header changed to the victim's `myshopify.com` domain. Since the library never binds `shop` into the signed content, the request passes `HmacValidator.validate` unchanged.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the material that is HMAC-verified for webhooks, or otherwise cryptographically bind the shop domain to the signed payload before trusting `request.shop` for tenant attribution — mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for the OAuth callback. At minimum, document that `Webhooks::Request#shop` is not authenticated by the HMAC and must be independently validated against expected/registered shops before being used for tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers/receives any webhook topic handled by the app.
2. Shopify sends a legitimately signed webhook to the app's endpoint:
   - Body: `{"id": 1, "note": "attacker controlled content"}`
   - Headers: `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`
3. Attacker replays this exact body+HMAC to the same public endpoint, only changing the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`= raw_body` only) and it matches — validation passes.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {...attacker content...}, ...)`, i.e., attacker-controlled data attributed to the victim's tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
