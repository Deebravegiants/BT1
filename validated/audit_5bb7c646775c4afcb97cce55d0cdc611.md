## Analysis Result [1](#0-0) , [2](#0-1) 

### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted for tenant/handler routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over that body alone, then trusts the unauthenticated `shop`, `topic`, and `webhook_id` header values to route the payload to a handler and stamp it with the tenant identity. Because the same `api_secret_key` is shared across every shop that has installed the app, any merchant who legitimately installed the app can capture one valid `(body, hmac)` pair from their own webhook deliveries and replay it with a forged `x-shopify-shop-domain`/`x-shopify-topic` header, and the gem will accept it as an authentic webhook "from" a different tenant.

### Finding Description
`Request#hmac` reads the received signature from the `hmac-sha256` header, while `Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`shop`, `topic`, and `webhook_id` are all read straight from unauthenticated HTTP headers, entirely outside of the signed string: [4](#0-3) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the received signature — i.e., it only binds the raw body to the secret, nothing else: [5](#0-4) 

`Registry.process` uses this validation as the sole authentication gate, then immediately trusts `request.topic` for handler dispatch and `request.shop` for the tenant identity forwarded to the handler: [2](#0-1) 

The identity binding that should hold is: `hmac-verified(secret, payload)` ⟹ `shop == the actual shop that sent this payload`. In this implementation, the binding only proves `hmac-verified(secret, raw_body)`; `shop`, `topic`, and `webhook_id` are unauthenticated headers that can be freely substituted while keeping `raw_body` and its valid `hmac` unchanged. Since `api_secret_key` is the same for every shop that installs a given app (it is the app's client secret, not a per-shop secret), a valid `(raw_body, hmac)` pair obtained from Shop A's genuine webhook delivery remains valid when replayed with `shop-domain: shop-b.myshopify.com` and any `topic` value.

### Impact Explanation
This breaks the shop/tenant identity boundary that `Registry.process` is relying on: an attacker who is a legitimate merchant of the app (and therefore able to trigger real webhook deliveries to their own shop, e.g. by creating an order, editing a product, or invoking any topic they've subscribed to) can capture one authentic `(body, hmac)` pair and replay it against the app's webhook endpoint while spoofing `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) to point at a victim shop. The receiving handler in `WebhookMetadata` is constructed straight from these spoofed headers: [6](#0-5) 

For a multi-tenant app, this is a cross-tenant identity spoof: application logic that keys off `data.shop` (e.g., updating billing state, writing to the victim's tenant record, processing `app/uninstalled` or GDPR `shop/redact` semantics, or writing attacker-supplied body content under the victim's shop record) can be triggered under a false tenant identity, using only a single legitimate app installation the attacker controls.

### Likelihood Explanation
Any user who can install the app on their own store (a normal, unprivileged action for a public/embedded Shopify app) automatically obtains a valid `(body, hmac)` pair whenever any subscribed webhook fires for their shop. No access to `api_secret_key`, access tokens, or victim credentials is required — only replaying an HTTP POST with modified headers. This is directly reachable through the gem's documented `Registry.process` entry point with no additional gem-level protections against shop/topic spoofing.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signed string (or otherwise cryptographically bind them, e.g., by validating that `shop` corresponds to a shop with an active, previously-stored session/installation before dispatching), rather than trusting header values that fall outside `to_signable_string`. At minimum, `Registry.process` should cross-check `request.shop` against a known/authorized shop registry before invoking the handler with that tenant identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the raw POST body and its `x-shopify-hmac-sha256` header — this is a valid `(body, hmac)` pair signed with the app's shared `api_secret_key`.
2. Attacker resends the exact same body and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `raw_body`, so the (unchanged) signature still validates:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
4. The handler executes believing the event originated from `victim-shop.myshopify.com`, even though that shop never sent it.

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
