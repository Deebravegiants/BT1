### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated HTTP headers, breaking the HMAC binding and enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler. Because the HMAC signature never covers these header values, any actor able to obtain one valid `(body, hmac)` pair signed with the app's shared `client_secret` — e.g. by installing the same app on their own shop and triggering an event with attacker-influenced body content — can replay that pair to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header, causing the app to process the payload as if it belonged to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read directly from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body), never over the shop/topic/webhook_id headers: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts `request.shop` (and the other unauthenticated header fields) to build the metadata handed to the app's own webhook handler: [4](#0-3) 

This breaks the identity binding: `hmac_verified(bytes) == raw_body`, but `shop_acted_on == header["x-shopify-shop-domain"]`, which is a disjoint, unauthenticated value. Since the signing secret (`api_secret_key`/`client_secret`) is shared by the app across **all** installing shops (it is not per-shop), any tenant that has installed the same app can legitimately obtain a `(body, hmac)` pair for body content they influence (e.g., by creating an order with a chosen note/line-item text in their own store, triggering `orders/create`). That pair remains HMAC-valid regardless of which `shop-domain` header accompanies it, because the header is never part of the signed content. An attacker can therefore submit that same valid body+HMAC directly to the app's public webhook route with the victim shop's domain in the header, and `Registry.process` will accept it and dispatch it to the handler as authentic data for the victim shop — a cross-tenant confusion/injection primitive.

### Impact Explanation
This is a cross-tenant data-integrity breach: an unprivileged attacker who is merely a legitimate tenant of the multi-tenant app (or who otherwise obtains one valid signed webhook body) can inject attacker-chosen webhook payloads attributed to any other shop known to use the app, without ever needing that victim's credentials or the app's `client_secret`. Any app logic that trusts `WebhookMetadata#shop` to select which merchant's records to update, delete, or sync will act on forged data under the wrong tenant, satisfying the "cross-tenant access" High-impact criterion.

### Likelihood Explanation
Exploitation requires: (1) the attacker being able to install/interact with the same app on any shop (a normal, unprivileged capability for anyone who can install a public Shopify app) to legitimately obtain one valid signed webhook body, and (2) the app's public webhook HTTP endpoint being reachable from the internet (a documented requirement of this gem's webhook usage). No access token, `api_secret_key`, or victim credentials are required, making this practically reachable by any external actor with an account able to install the target app.

### Recommendation
Include the values the application will act upon — at minimum `shop`, and ideally `topic`/`webhook_id` — in the HMAC-signed content, or independently verify `request.shop` against a shop the app has an active session/installation record for before trusting it. At a minimum, `Registry.process` (or the consuming app) should cross-check `request.shop` against known, previously-authenticated shop identities rather than accepting it as ground truth solely because the raw body's HMAC validated.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook event (e.g., `orders/create`) with attacker-chosen order data, causing Shopify to POST a legitimately HMAC-signed webhook to the app's public webhook endpoint. Capture the raw body and the `x-shopify-hmac-sha256` value.
3. Replay the exact same raw body and HMAC header to the same app webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12`) succeeds because it only checks the raw body against the shared secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188`) dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)` to the app's handler, which now processes attacker data under the victim shop's identity.

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
