### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the webhook HMAC to the raw request body only. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from HTTP headers — are never included in the signed material, yet `Registry.process` trusts these header-derived fields to build the `WebhookMetadata` object dispatched to the host application's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All of the identity-relevant accessors (`shop`, `topic`, `webhook_id`, `api_version`) are pulled straight from unauthenticated headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the body HMAC, then constructs `WebhookMetadata` directly from these unauthenticated header fields and passes it to the app's handler: [3](#0-2) 

Because the webhook secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that has installed the app, a valid `(raw_body, hmac)` pair proves only "this body/secret pair is authentic for *some* shop of this app" — it does not bind the body to the specific shop, topic, or webhook id claimed in the headers. This breaks the intended identity equality: `shop verified by HMAC == shop delivered to the handler`. In practice, `HmacValidator.validate` only checks `computed_signature(raw_body) == received_signature`: [4](#0-3) 

### Impact Explanation
Any entity capable of producing a valid `(raw_body, hmac)` pair for the app (e.g., a merchant/tenant who has the app installed on their own store and can capture/replay their own genuine webhook deliveries) can resubmit that same body while swapping the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to any other value. `Registry.process` will accept it as HMAC-valid and hand the host application a `WebhookMetadata` claiming the payload originated from a different, victim shop. Any host application logic that uses `WebhookMetadata#shop` to key merchant records, authorize data writes, or select per-tenant configuration would then attribute attacker-controlled data to another tenant — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one genuine `(body, hmac)` pair generated with the app's secret — most plausibly obtained by being a legitimate (but malicious) installer of the app on their own shop. No access to `api_secret_key`, access tokens, or other shops' credentials is required, and no changes to Shopify's request format are needed; only the delivered headers need to be altered before hitting the app's webhook endpoint, which is exactly the kind of unprivileged-tenant-to-cross-tenant boundary break in scope here.

### Recommendation
Do not treat header-derived `shop`, `topic`, `webhook_id`, or `api_version` as trusted merely because the raw-body HMAC validates. At minimum, document/require host apps to cross-check `shop` against session/shop records established during OAuth for that specific installation before acting on webhook data, and consider incorporating the shop domain into an application-level integrity check (e.g., verifying the shop is a known, currently-installed shop) rather than relying solely on the shared-secret body HMAC to imply per-shop authenticity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create` with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`).
2. Attacker resends the exact same body `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks `H` against `B`: [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed_body, ...)` and dispatches it to the host app's handler, which will treat attacker-controlled data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
