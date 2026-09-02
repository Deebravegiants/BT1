This confirms the vulnerability. `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only checks that the HMAC over `to_signable_string` (the raw body) matches, using the app's shared `api_secret_key` [3](#0-2) . `Registry.process` gates entirely on this HMAC check and then forwards `request.shop` straight to the handler as the tenant identity [4](#0-3) .

### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. Because `api_secret_key` is a single shared secret for the whole app (not per-shop), any request whose HMAC is valid for a given body remains valid regardless of which `shop-domain` header is attached, breaking the binding: `shop reported to handler == shop that produced/authorized the signed body`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors all pull straight from HTTP headers without any cryptographic binding to the signature [2](#0-1) . `HmacValidator.validate_signature` computes `HMAC(api_secret_key, to_signable_string)` and compares it to the `hmac` header value, entirely independent of the `shop` header [5](#0-4) . `Registry.process` uses this HMAC check as its sole authenticity gate before dispatching `request.shop` (attacker-controlled header) to the app's webhook handler [4](#0-3) .

Because `api_secret_key` is shared across every shop that installs the app (it is not per-shop, per-session), an attacker who installs the target app on their own shop can legitimately receive a genuinely-signed webhook (raw body + valid HMAC) for their own store. They can then replay that exact `raw_body`/`hmac-sha256` header pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (body and secret are unchanged), so `Registry.process` proceeds and calls the handler with `WebhookMetadata` claiming the forged victim `shop`, even though that shop never sent or authorized this event.

### Impact Explanation
This breaks the identity binding between the cryptographically-verified payload and the tenant (`shop`) the host application will act on behalf of. Any host app that uses `WebhookMetadata#shop` to look up/act on a merchant's data (e.g., fetch the merchant's stored session/access token, write to their store record, trigger merchant-scoped side effects) can be tricked into performing actions attributed to, or affecting, a shop the attacker does not own — a cross-tenant confusion vulnerability reachable by any unprivileged internet user who can install the app once on their own store.

### Likelihood Explanation
High likelihood: the attacker only needs to be able to install the target app on a shop they control (a standard, unprivileged action for any Shopify merchant/developer) in order to obtain one genuinely HMAC-signed webhook body they can replay with a spoofed `shop-domain` header against the shared, public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signed content, or otherwise cross-check the header-derived `shop` against an independently authenticated source (e.g., verify the webhook via the GraphQL Admin API or reconcile against the shop associated with the specific `webhook_id`) before dispatching to handlers. At minimum, document that host applications must not trust `WebhookMetadata#shop` without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the request to the app's webhook endpoint, keeping `raw_body = B` and `hmac-sha256 = H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, B)`, which equals `H`, so validation passes [6](#0-5) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, spoofing the tenant identity for the app's business logic [7](#0-6) .

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
