### Title
Webhook `shop` identity is read from an unauthenticated header while `HmacValidator` only signs the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` only returns the raw body bytes, never the `shop`, `topic`, `webhook_id`, or `api_version` headers. `Registry.process` treats a passing `HmacValidator.validate` result as proof that the *entire* webhook request — including `request.shop` — is authentic, and forwards `request.shop` straight into `WebhookMetadata` for the app's handler. In reality, the HMAC only proves the body bytes were signed by holders of `api_secret_key`; it says nothing about which shop the header claims to be from.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the raw JSON body is fed into the HMAC comparison, while `shop` is pulled directly, unauthenticated, from the `x-shopify-shop-domain` header: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it against the `hmac` header via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authenticity gate before dispatching, and passes the unauthenticated `request.shop` header value straight through to the app's handler as trusted metadata: [4](#0-3) 

The identity binding that should hold is: `shop asserted in WebhookMetadata == shop cryptographically bound by the HMAC`. Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (it is not per-shop), any entity that can obtain one valid `(raw_body, hmac)` pair for *some* shop — for example, by installing the app on their own store and triggering any webhook-eligible event — possesses a fully valid signature for that exact body. They can then replay that body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still passes (it never looks at the shop header), so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain while the body content actually originated from the attacker's own shop.

### Impact Explanation
This breaks the tenant boundary the library is expected to enforce: an unprivileged merchant who has installed the app on their own store can forge webhook events that `Registry.process` reports as coming from a *different* shop. Any app logic that uses `WebhookMetadata#shop` to select which tenant's data to update (a very common pattern, since `shop` is the natural partition key) can be tricked into applying attacker-controlled body content under another merchant's identity — i.e., cross-tenant data injection/corruption via the gem's own trusted-metadata contract. This matches the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Any developer/merchant who can install the target app on a shop they control satisfies the prerequisite (no leaked credentials, no privileged account, and no reliance on the host app misusing the library — the vulnerable trust boundary is inside `Request`/`Registry` themselves). Triggering at least one webhook (e.g. `products/create`) is trivial and gives the attacker a valid `(body, hmac)` pair signed with the app's shared secret. Replaying it with a modified `shop-domain` header requires nothing more than basic HTTP tooling.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cross-check the value against an out-of-band trusted source (e.g., verify the shop is a session/shop the app actually has an active installation for) before trusting `WebhookMetadata#shop`. At minimum, document clearly that `request.shop` is unauthenticated and must not be used as a tenant-selection key without additional verification.

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; attacker triggers any subscribed webhook (e.g. updates a product), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sends — both are valid under the app's single, shared `api_secret_key`.
2. Attacker POSTs the identical `raw_body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body) == hmac` — this passes because both are unchanged from step 1.
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's body>, ...)` and invokes the app handler, which now processes attacker-controlled content under `victim.myshopify.com`'s identity.

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
