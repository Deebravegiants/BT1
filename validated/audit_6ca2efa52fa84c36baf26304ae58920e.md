## Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop`, `topic`, and `webhook_id` values are read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC exclusively against this body-only signable string [1](#0-0) , so the `shop` header that `Registry.process` later trusts to attribute the event to a tenant is never covered by the signature [2](#0-1) .

### Finding Description
The equality the gem is supposed to enforce is:

`hmac_signed_bytes == (body, shop, topic, webhook_id)`

but the actual signed content is only:

`hmac_signed_bytes == (body)`

`Request#shop`, `#topic`, and `#webhook_id` are pulled straight from the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` HTTP headers [3](#0-2) . None of these headers participate in `to_signable_string`, which only returns `@raw_body` [1](#0-0) . `HmacValidator.validate` computes the signature purely from this signable string and the app's `api_secret_key`, comparing it to the `hmac` value (itself also header-derived) [4](#0-3) . Once that check passes, `Registry.process` hands `request.shop` directly to the app's handler as the tenant identifier with no additional validation [2](#0-1) .

This is inconsistent with the gem's own OAuth callback path, where the equivalent `AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameter set [5](#0-4) , correctly binding the shop identity to the signature. The webhook path lacks this binding.

Because the same `client_secret`-derived HMAC is valid for every shop that installs the app, an attacker who legitimately installs the app on their own store (a fully unprivileged action requiring no special credentials) will receive genuine `(body, hmac)` pairs from Shopify. That attacker can then POST the identical body and HMAC directly to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim's shop). `HmacValidator.validate` still succeeds because the header is not part of the signed content, and `Registry.process` will invoke the app's handler believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant-authentication binding between "the shop that produced the signed bytes" and "the shop the app attributes the event to," enabling cross-tenant data injection: an attacker can make the host application write/process data (e.g., order/customer webhook payloads) under another merchant's identity, corrupting that tenant's state or triggering tenant-scoped side effects (state changes, downstream jobs, notifications) attributed to a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on any shop (an ordinary, unprivileged action any Shopify merchant can perform), (2) capturing one legitimate webhook delivery for that shop, and (3) replaying the exact body/HMAC to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or any privileged credential is required, making this practically reachable by any unprivileged internet user who can install a free/dev store.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed content verification, or otherwise cryptographically bind the declared shop domain to the signed payload before it is trusted by `Registry.process`. At minimum, cross-check `request.shop` against a shop known to have a valid, previously established session/install record before dispatching to the handler, rather than trusting the header solely because the body-only HMAC validated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook delivery:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-topic: orders/create`
   - Body: `{"id": 1, ...}`
2. Attacker resends this exact body and `x-shopify-hmac-sha256` value directly to the app's public webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` recomputes the HMAC over `to_signable_string` (body only), matches the unchanged `hmac`, and returns `true` [6](#0-5) .
4. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` even though the payload never actually came from or was signed in the context of that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
