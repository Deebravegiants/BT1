### Title
Webhook shop/topic identity forgery via HMAC that only signs the body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` and `topic` headers — which are never covered by that HMAC — to the app's handler as if they were verified merchant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors simply read the corresponding HTTP headers verbatim, with no cryptographic binding to the signature: [2](#0-1) .

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., HMAC-SHA256 over the raw body using `Context.api_secret_key`), then routes purely on `request.topic` and forwards `request.shop` straight into `WebhookMetadata` passed to the handler: [3](#0-2) .

`HmacValidator.validate` performs `OpenSSL.secure_compare` of the computed HMAC of `verifiable_query.to_signable_string` against the received HMAC — for a `Webhooks::Request`, that signable string is only the body: [4](#0-3) .

The broken identity binding is: `HMAC(raw_body)` valid ⇒ (`shop`, `topic`) trustworthy. In reality, `shop` and `topic` are independent, attacker-controllable header bytes that are never part of the signed material. Because a single app-level `api_secret_key` is shared across *every* shop that installs the app, any merchant who legitimately installs the app can capture one genuine `(raw_body, hmac)` pair from a real webhook Shopify sends them (e.g., for `orders/create`), then replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain (and keeping/matching the `topic` header to route to the desired handler). `Registry.process` will pass HMAC validation (since the body+secret combination is genuinely valid) and will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem hands a handler data attributed to `shop` = attacker-chosen value while only the body bytes were authenticated. Any host application that uses `WebhookMetadata#shop` to determine which merchant's data to update, delete, or reconcile (a documented, expected usage pattern — see `docs/usage/webhooks.md`'s `handler.handle(data:)` example) can be tricked into acting on a forged tenant identity, enabling cross-tenant data corruption, spoofed uninstall/GDPR events, or state confusion between merchants — this maps to the "Critical - cross-tenant access" impact tier.

### Likelihood Explanation
Requires only: (1) attacker to be a legitimate (self-serve) install of the same public app on their own shop — a standard unprivileged capability for public Shopify apps — to obtain one genuinely-signed `(raw_body, hmac)` pair, and (2) the ability to POST an HTTP request to the app's public webhook endpoint with a forged `shop-domain` header, which any internet client can do since the endpoint is a normal unauthenticated HTTP route. No possession of `api_secret_key` or any victim credential is required.

### Recommendation
Bind the webhook's tenant/topic identity into the authenticated material, e.g., include `shop`, `topic`, and `webhook_id` header values in the signable string used for HMAC comparison (or otherwise cryptographically bind them), so that tampering with those headers invalidates the signature. At minimum, `Registry.process` should not trust `request.shop`/`request.topic` unless they are covered by the verified signature.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it trigger any registered webhook topic (e.g., `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify legitimately computed with the app's shared `api_secret_key`.
2. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with:
   - Body: the exact same bytes `B`
   - Header `shopify-hmac-sha256`: the exact same value `H`
   - Header `shopify-topic`: `orders/create`
   - Header `shopify-shop-domain`: `victim.myshopify.com` (forged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(B, api_secret_key)` and matches `H` — validation passes (per `lib/shopify_api/utils/hmac_validator.rb`).
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "orders/create", body: parsed(B), ...)` (per `lib/shopify_api/webhooks/registry.rb` lines 188-199), even though `victim.myshopify.com` never sent this webhook and its data was never authenticated.

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
