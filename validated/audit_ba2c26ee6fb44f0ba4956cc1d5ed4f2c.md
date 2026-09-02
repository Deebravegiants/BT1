### Title
Webhook `shop` identity is parsed from an unauthenticated HTTP header and never covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking the HMAC of the raw request body only. The `shop` (and `topic`/`webhook_id`/`api_version`) values that are handed to the integrating app's handler as the authoritative tenant identity come from HTTP headers that are completely outside the HMAC's signed content. This breaks the identity binding `shop authenticated == shop acted upon`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from headers, with no participation in the signature at all: [2](#0-1) 

`Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., the body) and compares it against the computed HMAC over the body: [3](#0-2) [4](#0-3) 

After this "valid" check, `request.shop` (an unauthenticated header) is forwarded straight into `WebhookMetadata`, which is the object the host application's handler uses to determine which tenant/shop the event pertains to: [5](#0-4) [6](#0-5) 

This is a deliberate design elsewhere in the same gem for the OAuth callback: `Auth::Oauth::AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameter set, binding the authenticated shop to the HMAC: [7](#0-6) 

The webhook path has no equivalent binding — `bytes verified` (body only) ≠ `bytes/fields parsed and trusted` (`shop`, `topic`, `webhook_id`, `api_version` headers).

### Impact Explanation
Any party who can obtain one genuine `(raw_body, x-shopify-hmac-sha256)` pair for a webhook topic (e.g., by legitimately installing the target app on their own store and receiving real Shopify webhooks) can replay that exact body+signature to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The HMAC check will still pass because it never examined the header. The gem then constructs a `WebhookMetadata` claiming the event is for the attacker-chosen shop, and the handler executes application logic (e.g., updating billing state, disabling features, writing to per-shop records) attributing the event to a victim tenant it was never actually generated for. This is a cross-tenant identity-confusion primitive delivered entirely through this gem's own webhook-processing API, requiring no access token, `api_secret_key`, or privileged access — only the ability to receive one legitimate webhook for any shop (including the attacker's own) and replay it with a modified header.

### Likelihood Explanation
Exploitation requires no secrets: an attacker installs the target app on a shop they control (a normal, unprivileged action available to anyone), captures a real webhook delivery for a topic of interest, and replays it to the app's public webhook endpoint with a forged `shop-domain` header (and optionally forged `topic`/`webhook-id`). Because header-content spoofing over plain HTTP requires no cryptographic material, the barrier to exploitation is low, though its exact impact fully depends on how a given host application handles `WebhookMetadata#shop` (e.g., whether it uses it to select which shop's session/data to mutate) — a factor outside this gem's control but is exactly the trust the gem's API is expected to provide.

### Recommendation
Include the identity-relevant headers (at minimum `shop`, and ideally `topic`/`webhook_id`) as part of the HMAC-signed content that `Request` verifies, or independently verify the `shop` value against Shopify's documented webhook payload/shop fields before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is derived from an unauthenticated header and must not be trusted as tenant-binding without secondary verification against session data.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a real webhook, e.g. `orders/create`, capturing:
   - raw body `B`
   - header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's real secret, computed by Shopify)
   - header `x-shopify-shop-domain: attacker.myshopify.com`
2. Attacker sends a new HTTP request to the app's webhook endpoint with the *same* body `B` and *same* HMAC header `H`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Request.new` parses headers, `Registry.process` calls `HmacValidator.validate(request)`; validation succeeds because it only hashes `B` [1](#0-0) [8](#0-7) .
4. `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` is passed to the app's handler [9](#0-8) , causing the application to act as if the event originated from `victim.myshopify.com`, despite it never sending this webhook.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
