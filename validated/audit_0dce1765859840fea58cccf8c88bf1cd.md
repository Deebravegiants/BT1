### Title
Webhook `shop` identity is taken from an unauthenticated HTTP header, not from the HMAC-covered payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#shop` returns the value of the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while HMAC validation (`Utils::HmacValidator.validate`) only signs and verifies `@raw_body` (`to_signable_string`). The tenant identity (`shop`) that gets handed to the app's `WebhookHandler#handle` is therefore not part of the authenticated bytes, breaking the binding: `hmac_verified_bytes == raw_body` while `tenant_identity_used == header["shopify-shop-domain"]`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose contract is `hmac` + `to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw request body: [2](#0-1) 

`shop` (the tenant identifier) is read from a header instead, and is not part of the signable string: [3](#0-2) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes an HMAC over `to_signable_string` (i.e., only `raw_body`) and compares it to the `hmac` header - `shop` plays no role in this computation: [4](#0-3) 

After the HMAC check passes, `request.shop` (header-derived, unauthenticated) is passed straight into `WebhookMetadata` and handed to the app's handler as the trusted tenant identity: [5](#0-4) [6](#0-5) 

So the equality that should hold - `shop bound by HMAC == shop used to key the tenant's data/session` - does not hold. Instead: `HMAC verifies raw_body only`, while `shop (tenant key) is taken from an unsigned header`, letting anyone who can produce one valid `(raw_body, hmac)` pair (e.g., via a webhook that their own installed app instance legitimately received from Shopify) resubmit that exact body/hmac pair to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header. The HMAC check still passes because it never inspected `shop`, yet the host app will process that body as if it belonged to whatever shop the attacker names in the header, since it's the only "shop" the gem exposes from a validated webhook `Request`.

### Impact Explanation
This breaks the identity binding between the cryptographically-verified bytes and the tenant the app records/acts on for that webhook (`WebhookMetadata#shop`). Depending on what the host app does in its `WebhookHandler#handle` (e.g., updating shop records, disabling/removing shop data on `app/uninstalled`, or writing customer data on `customers/data_request`/`shop/redact`), an attacker who has legitimate (even free/unprivileged) access to their own shop's app installation can cause cross-tenant data confusion by replaying a legitimately-signed webhook body under a spoofed `shop` header, since the gem gives the host application no way to distinguish "the shop the HMAC-signed body came from" versus "the shop named in the header." This matches the Critical "cross-tenant access" impact category, since it lets one merchant's webhook traffic be misattributed to a different merchant's tenant record purely by manipulating an unauthenticated header.

### Likelihood Explanation
Exploitability depends entirely on the attacker being able to obtain at least one valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`. An unprivileged user who installs the app on their own store receives legitimate Shopify webhooks (with valid HMACs) addressed to their own shop. They fully control the HTTP request they replay to the app's webhook endpoint (headers are not authenticated), so they can trivially swap `shopify-shop-domain` (and any `x-shopify-*` id headers) while keeping the original signed body+HMAC. No access token, `client_secret`, or privileged account is required - only ordinary use of their own app installation. This is a low-effort, credential-free attack path once the app is installed on any store the attacker controls.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified, or otherwise have `HmacValidator`/`Registry.process` cross-check the header-derived `shop` against a shop identifier embedded in (or otherwise bound to) the signed payload before it is exposed to `WebhookHandler#handle`. At minimum, document prominently that `Request#shop` is unauthenticated and must not be trusted as a tenant key without an out-of-band check (e.g., against a per-shop webhook secret, or comparing to a previously known/allow-listed shop for that app installation) before it is used to select tenant state.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, e.g. `customers/data_request`, capturing:
   - Raw body `B`
   - Valid header `X-Shopify-Hmac-Sha256: H` (HMAC over `B` with the app's real `api_secret_key`)
2. Attacker resends the exact same HTTP request to the app's webhook endpoint, but replaces the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - keeps the same body `B` and `X-Shopify-Hmac-Sha256: H`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and finds it matches `H` — validation passes: [7](#0-6) 
4. `request.shop` returns `"victim-shop.myshopify.com"` from the spoofed header: [3](#0-2) 
5. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's own shop's data>, ...)` is passed to the host app's handler, which will process the attacker-controlled body as belonging to `victim-shop.myshopify.com`, corrupting/overwriting that shop's tenant-scoped state with the attacker's data: [8](#0-7)

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-15)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
