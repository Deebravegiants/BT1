### Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only checks that the HMAC matches the body bytes, never binding it to the `shop-domain` header, so the shop identity attached to a webhook is not cryptographically tied to the signature that authenticates it.

### Finding Description
`Request#hmac` is derived from the `hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the supplied header value: [2](#0-1) 

`Registry.process` treats a successful `HmacValidator.validate` as proof the entire request — including `request.shop` — is authentic, and forwards `request.shop` straight to the app's handler as the tenant identity: [3](#0-2) 

The binding that should hold is:
`hmac == HMAC(secret, body || shop || topic || ...)`
but what is actually verified is:
`hmac == HMAC(secret, body)` while `shop` (and `topic`, `webhook_id`, `api_version`) are read from headers that are never covered by the signature.

Because `shop-domain` is excluded from the signed bytes, any party who can obtain one valid `(raw_body, hmac)` pair — trivially available to anyone who installs the app on their own development/trial store and receives one genuine webhook — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g. a victim merchant's domain). `HmacValidator.validate` will still return `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook authentication scheme is supposed to provide: the HMAC is meant to prove "this event genuinely originated from Shopify for this shop," but an unprivileged internet user (only needing their own low-privilege shop install) can forge events attributed to any other shop. Host applications built on this gem reasonably treat `WebhookMetadata#shop`/`request.shop` as trustworthy once `HmacValidator.validate` passes (that is the documented purpose of the validation call), so this enables cross-tenant data injection/attribution — e.g., triggering shop-scoped side effects (data deletion, state changes, cache invalidation, order/customer processing) against a victim shop, or forcing execution of mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) against a shop the attacker doesn't own.

### Likelihood Explanation
High likelihood: the only prerequisite is a working `client_secret`-free relationship — an attacker installs the target app on any shop they control (including a free/dev store), captures one legitimate webhook body+HMAC pair from Shopify, and replays it to the app's public webhook endpoint with a different `shopify-shop-domain` header. No access to the app's `client_secret`, no victim credentials, and no privileged access are required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable bytes checked against the HMAC, or independently verify that the shop present in the payload/headers matches an expected/allow-listed shop before trusting `request.shop`/`WebhookMetadata#shop`. At minimum, document and enforce that `shop-domain` must be authenticated by cross-checking it against the shop for which the app has an active, HMAC-validated installation, rather than trusting the header solely because the body-only HMAC passed.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they legitimately control) and triggers any webhook (e.g. `orders/create`), capturing the raw body `B` and the valid `shopify-hmac-sha256` header value `H` Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim-shop.myshopify.com", "shopify-hmac-sha256" => H})` is constructed.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this succeeds because `B` and `H` are unmodified and genuinely matched.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the app processes an attacker-crafted event as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
