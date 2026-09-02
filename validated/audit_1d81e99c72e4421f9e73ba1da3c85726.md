## Title
Webhook `shop` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs (for HMAC verification purposes) only the raw request body, while the `shop`, `topic`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` uses to route and attribute the webhook to a tenant are read from unauthenticated HTTP headers that are never part of the HMAC-covered bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC solely over `verifiable_query.to_signable_string` (i.e. body-only for webhooks) and secure-compares it against the caller-supplied `hmac` header: [3](#0-2) 

`Registry.process` then trusts the unauthenticated `request.shop` value to build the `WebhookMetadata` handed to the app's handler, using only the body-HMAC result as its authentication gate: [4](#0-3) 

Because the app's `api_secret_key` (`client_secret`) is shared across every shop that installs the app, any tenant that has legitimately installed the app can capture a validly HMAC-signed webhook body Shopify sent for their *own* shop, then replay it against the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (and `Topic`/`Webhook-Id`) header rewritten to point at a *different* victim shop. `Utils::HmacValidator.validate` will still return `true`, because the signature check never touches those headers — the equality the gem should enforce, `hmac_signed(shop) == shop_used_by_handler`, silently degrades to `hmac_signed(body) == raw_body`, with `shop` entirely outside the trust boundary.

### Impact Explanation
This breaks the tenant boundary the whole `Session`/webhook model is built on: a host application that keys anything (session lookup, DB writes, entitlement checks) off `WebhookMetadata#shop` as returned by this gem can be made to process attacker-controlled webhook content under a victim shop's identity, despite `HmacValidator.validate` reporting success. This is cross-tenant access via a credential-binding gap inside the gem's own webhook-verification code path, not a host-app misuse of a documented API — the gem's `Registry.process`/`Request` classes are the ones responsible for authenticating and exposing `shop`.

### Likelihood Explanation
Exploitation only requires being an unprivileged merchant/tenant who has installed the target app (a normal, unprivileged action) and the ability to send an HTTP POST to the app's public webhook URL with modified headers and a previously-observed valid body+HMAC pair for a topic they control (e.g. `orders/create` on their own shop). No access token, `client_secret`, or privileged account is required.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-covered signable string for webhook requests, or otherwise cryptographically bind them to the verified payload, so `Utils::HmacValidator.validate` cannot succeed for a body that was signed for one shop but relabeled for another.

### Proof of Concept
1. Install the target app on attacker-controlled shop A; capture a legitimate webhook POST (raw body `B` and header `X-Shopify-Hmac-Sha256: H`), which Shopify signed with the app's single `api_secret_key`.
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only (`to_signable_string` at `lib/shopify_api/webhooks/request.rb:36-38`) and returns `true` since `B`/`H` are unchanged.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to process attacker data as if it originated from the victim tenant.

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
