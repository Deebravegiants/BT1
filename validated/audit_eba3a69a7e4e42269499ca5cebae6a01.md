### Title
Webhook `shop`/`topic`/`webhook_id` fields are trusted for cross-tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` but its `to_signable_string` returns only the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id` and `api_version` values are read directly from HTTP headers and are never included in the HMAC-verified data [2](#0-1) . `Registry.process` validates only the body HMAC and then dispatches the handler using these unauthenticated header values [3](#0-2) , so the identity binding "shop the HMAC was computed for" == "shop the handler acts on" does not hold.

### Finding Description
This is the same bug class as the reference report: a value that is *acted on* (here, `request.shop`, `request.topic`, `request.webhook_id`) is not covered by the cryptographic check that is supposed to authenticate the message (`Utils::HmacValidator.validate`, which only signs/verifies `to_signable_string`, i.e., the raw body) [4](#0-3) .

Because Shopify signs webhooks with the app's single, shop-independent `api_secret_key` (the same secret is used for every shop that installs the app), any party that can obtain one legitimately-signed `(body, hmac)` pair — for example, by installing the app on their own store and receiving a real webhook — holds a valid HMAC for that exact body. Nothing in this library prevents that same `(body, hmac)` pair from being replayed to the app's webhook endpoint with a different `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` header, since `Request#to_signable_string` never includes them [5](#0-4) . `Registry.process` will accept the request (HMAC check passes because it only checks the body) and forward the attacker-chosen `shop`/`topic`/`webhook_id` straight to the registered handler [6](#0-5) .

The equality that should hold — `hmac_verified(shop, topic, body) == handler_acted_on(shop, topic, body)` — is broken to `hmac_verified(body) != handler_acted_on(shop, topic, body)`.

### Impact Explanation
Handlers built on top of `WebhookMetadata` are expected to trust `data.shop` and `data.topic` as identifying which tenant/store an event belongs to (this is explicitly how `MANDATORY_TOPICS` such as `shop/redact` and `customers/redact` are dispatched [7](#0-6) ). An attacker who can obtain any one valid `(body, hmac)` pair for the shared app secret (e.g., from their own store's install) can forge a POST to the app's webhook endpoint claiming it originates from a different shop or a different topic, since neither is authenticated. This is a cross-tenant identity-binding failure: the app cannot distinguish "this HMAC-valid payload really describes shop X" from "attacker replayed a valid payload under shop Y's name." Depending on how the host app's handler uses `shop`/`topic` (e.g., triggering GDPR data deletion, uninstall cleanup, or state changes keyed by `shop`), this can lead to cross-tenant data corruption/deletion or spoofed lifecycle events for a victim shop.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint plus one legitimately obtained `(body, hmac)` pair, which any unprivileged user who installs the target app on a store they control can acquire (installing an app on one's own dev/test store is an "unprivileged internet user" action, not a privileged credential). No access token, `client_secret`, or victim credentials are needed — only replay of a previously-observed valid signature with different headers. This keeps it within the rules' allowed unprivileged-attacker model.

### Recommendation
Include the values the handler will act on (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before verification, so that `to_signable_string` reflects everything `Registry.process` subsequently trusts. At minimum, `Request#to_signable_string` should be extended (or a secondary check added) so that the shop/topic used for dispatch cannot be altered independently of the verified payload.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. topic `customers/redact` with body `B` and header `x-shopify-hmac-sha256: H` (valid because it's HMAC-SHA256(`B`, `api_secret_key`) — same secret for all shops).
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and the same `hmac` header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (or a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Utils::HmacValidator.validate(request)` returns `true` because it only validates `@raw_body` against `H` [1](#0-0) .
4. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with the attacker-controlled `shop`/`topic` values [8](#0-7) , causing the host app to act as if the event came from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
