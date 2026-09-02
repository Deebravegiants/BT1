### Title
Webhook shop identity is not covered by HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook solely by validating the HMAC over the raw request body, while the `shop` (and `topic`) that the rest of the library trusts and hands to the app's handler are read from unauthenticated HTTP headers that are never part of the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are pulled straight out of the `shopify-shop-domain` / `shopify-topic` headers, with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC and then dispatches using `request.shop` taken from that same unauthenticated header: [3](#0-2) 

`Utils::HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`, i.e. the raw body, when computing/comparing the signature: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used by the handler to act on tenant data`. Because the `shopify-shop-domain` header is excluded from `to_signable_string`, this equality is never enforced — the HMAC only proves "this body was produced with our `api_secret_key`", not "this body belongs to shop X". A holder of any one valid `(raw_body, hmac)` pair — which any merchant/attacker who installs the app on their own shop can legitimately obtain from a real Shopify-sent webhook — can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header value. HMAC validation still succeeds because it never inspected the header, and `Registry.process` will hand the (unrelated) attacker-controlled body to the handler tagged with the victim shop's domain.

### Impact Explanation
This is a cross-tenant identity confusion in the gem's own webhook trust boundary: the field the host application is documented to rely on for tenant scoping (`WebhookMetadata#shop`, populated from `request.shop`) is not covered by the authenticity check the gem performs. An attacker who has any working `(raw_body, hmac)` pair (trivially obtainable by installing the app on their own store and capturing one of Shopify's legitimate webhook deliveries) can cause the library to report that data for an arbitrary victim shop, since `Registry.process` never re-validates the header against the signed content. Applications that key their per-tenant logic (data lookups, session retrieval, mandatory GDPR redact/data-request handling, etc.) off of `request.shop`/`WebhookMetadata#shop` as intended by this API can therefore be tricked into treating attacker-supplied data as belonging to a different tenant — a cross-tenant access condition rooted entirely in this gem's verification logic, not application misuse.

### Likelihood Explanation
Exploitation requires no secrets: any actor able to install the target app on a shop they control receives real, validly-signed webhooks and thus obtains a valid `(raw_body, hmac)` pair without ever needing `api_secret_key`. Forging or replaying HTTP headers alongside a previously captured body is trivial for any internet-facing webhook endpoint, since `Registry.process`/`HmacValidator.validate` do not bind headers to the signature.

### Recommendation
Include the shop domain (and topic/webhook id, as applicable) in the HMAC-signed material, or independently verify that the `shopify-shop-domain` header matches a value cryptographically tied to the signed payload, before trusting `request.shop` in `Registry.process`. At minimum, document/verify that host apps must not trust `WebhookMetadata#shop` without additional out-of-band tenant verification, since the gem currently provides no such binding.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook Shopify sends the app, e.g. body `{"id":1}` with headers `shopify-hmac-sha256: <valid-hmac-for-body>`, `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: customers/redact`.
2. Replay the exact same body and `shopify-hmac-sha256` value to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` (called from `Registry.process`, see [5](#0-4) ) recomputes the HMAC over `@raw_body` only and it matches — validation passes.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `request.shop` now resolves to `"victim.myshopify.com"` even though the HMAC never authenticated that value, causing the app to process/redact data under the wrong tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
