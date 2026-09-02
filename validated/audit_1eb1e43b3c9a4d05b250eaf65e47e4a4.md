### Title
Webhook HMAC validation only covers the raw body, allowing the `shop-domain` (and other) headers to be forged independently of the signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking that the HMAC over the **raw body** matches the `x-shopify-hmac-sha256` header. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers that the handler is handed as the trusted tenant/context identifiers are never included in the signed material, so any attacker who can obtain one validly-signed `(raw_body, hmac)` pair can replay it while freely substituting a different `shop-domain` header and have it accepted as an authentic webhook "from" that other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All the other identifying fields (`shop`, `topic`, `api_version`, `webhook_id`) are parsed straight from the unauthenticated HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only ever hashes `verifiable_query.to_signable_string` (i.e. the body) and compares it to the received HMAC: [3](#0-2) 

`Registry.process` gates on that same body-only check and then forwards the unauthenticated `request.shop` value straight into the handler as `WebhookMetadata.shop`: [4](#0-3) 

The equality the gem's API implicitly promises to callers is:
`hmac_valid? == (shop, topic, body all came from Shopify for this delivery)`

But the equality it actually enforces is only:
`hmac_valid? == (this exact raw_body byte string was signed with the shared secret at some point)`

Because `shop`, `topic`, `webhook_id`, and `api_version` are excluded from the signed string, a party who legitimately receives one valid webhook delivery for their own tenant (e.g., an app developer/merchant who installs the app on their own store, a completely unprivileged action) can capture that `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header value. `Utils::HmacValidator.validate` will still return `true` because it never inspects the shop header, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen value.

### Impact Explanation
Any app whose webhook handler uses `data.shop` from `WebhookMetadata` (as documented/intended in `docs/usage/webhooks.md`) to select or scope the tenant record being created/updated will process an attacker-controlled payload under a victim shop's identity — a cross-tenant data-integrity/confusion issue triggered purely by an unprivileged party who can trigger any real webhook delivery to their own shop and replay it. This matches the Critical "cross-tenant access" category since the tenant boundary (`shop`) is not actually bound to the authenticated bytes.

### Likelihood Explanation
Requires only that the attacker (a normal, unprivileged merchant/developer who can install the target app on their own store) receive one real webhook delivery and be able to reach the app's public webhook endpoint — no access token, `client_secret`, or privileged access is needed. The mechanics (header vs. body binding gap) are inherent to the shipped `Request`/`HmacValidator` implementation, not a host-application misuse.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable material used for HMAC verification (or otherwise cryptographically bind them, e.g. by hashing `raw_body + shop + topic` together), so `Utils::HmacValidator.validate` fails whenever any of these fields is altered relative to what Shopify actually sent, not just when the body changes.

### Proof of Concept
1. Attacker installs the app on their own (unprivileged) development shop `attacker.myshopify.com` and triggers any webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and some `raw_body`.
3. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (only checking `raw_body`) returns `true`; `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim.myshopify.com"`, as shown in: [5](#0-4) 
5. Any app logic keyed on `data.shop` now processes attacker-controlled data attributed to the victim shop.

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
