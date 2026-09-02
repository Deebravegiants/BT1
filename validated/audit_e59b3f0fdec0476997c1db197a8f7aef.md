### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` binds solely to the request body. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the signed material, yet `Registry.process` trusts `request.shop` as the authoritative tenant identity passed to the app's `WebhookHandler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all derived from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.): [1](#0-0) 

The HMAC validity check, however, is computed only from `to_signable_string`, which returns `@raw_body` and nothing else: [2](#0-1) 

`HmacValidator.validate` verifies the signature strictly against `to_signable_string`: [3](#0-2) 

`Registry.process` calls this validator, then immediately trusts `request.shop` (a header value not covered by the HMAC) as the tenant identity forwarded to the app's handler: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated by HMAC == shop delivered to handler`. In reality, only `raw_body` is authenticated; `shop` (and `topic`/`webhook_id`) are parsed from headers with zero cryptographic binding. This is exactly the "field acted on but not covered by the HMAC" class: an attacker who can obtain any one valid `(raw_body, hmac)` pair signed with the app's secret (e.g., by installing the app on their own shop and capturing a legitimate webhook delivery addressed to them) can replay that same body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for an arbitrary victim shop domain. `HmacValidator.validate` will still return `true` because the signature check never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop`, `host`, `code`, `state`, and `timestamp` in the signed string, correctly binding those fields to the HMAC: [5](#0-4) 

The webhook path has no equivalent binding for `shop`/`topic`/`webhook_id`.

### Impact Explanation
An app built on this gem that uses `WebhookMetadata#shop` to key data (e.g., "process this order/customer/GDPR payload for shop X", store data under shop X's tenant, or trigger shop-scoped side effects) can be made to process attacker-supplied payloads under an arbitrary victim shop's identity, without the attacker ever possessing that shop's data or the app's `client_secret`. This is a cross-tenant data injection / cross-tenant access vulnerability: the "authenticated" shop (the one whose secret validated the HMAC — the app's own client secret, shared across all merchants) is not equal to the shop actually recorded and acted upon (`request.shop` from the header), and the gem provides no mechanism to bind them.

### Likelihood Explanation
Exploitation requires the attacker to have installed the app themselves (or otherwise obtained one legitimate `(body, hmac)` pair for any shop using that app instance), which is an ordinary unprivileged action available to any internet user who can install a public app. No leaked secret, TLS interception, or privileged account is required — only the ability to (a) become an install target of the app to receive one legitimate webhook, and (b) send a crafted HTTP POST directly to the app's public webhook endpoint with a substituted `shop-domain` header and the replayed body/HMAC.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material verified against the HMAC (or otherwise cryptographically bind them, e.g., by validating them against Shopify's IP allowlist or mTLS, or by additionally checking that the shop domain matches an expected/known installed shop before trusting `WebhookMetadata#shop`). At minimum, document clearly that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are unauthenticated header values and must not be trusted as tenant identifiers without additional application-level verification (e.g., cross-checking against the app's own stored session/shop list).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (normal, unprivileged action).
2. Shopify sends a legitimate webhook to the app's endpoint with body `B`, and headers including `shopify-hmac-sha256: H` (valid for `B` under the app's secret) and `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H` (they own this delivery/endpoint or can capture it via their own logging).
4. Attacker crafts a new HTTP POST directly to the app's public webhook endpoint with the same body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object; `HmacValidator.validate(request)` computes `compute_signature(request.to_signable_string, secret)` = `compute_signature(B, secret)`, which still equals `H`, so validation passes. [6](#0-5) 
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
