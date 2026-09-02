### Title
Webhook shop/topic identity fields are unauthenticated relative to the HMAC signature, enabling cross-tenant webhook attribution spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string` (the body) [3](#0-2) , and `Registry.process` accepts the request once that check passes and then dispatches `request.shop`/`request.topic` straight to the host app's handler without any further binding to the signed content [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header == shop that produced/authorized the signed body`. In this implementation, the HMAC only proves "this body was produced with knowledge of `api_secret_key`" — it says nothing about which shop, topic, or webhook id the body belongs to, because those fields are excluded from `to_signable_string`. Since the webhook HMAC secret (`Context.api_secret_key`) is a single app-level secret shared by every shop that installs the app, any unprivileged internet user who installs the app on their own (attacker-controlled) shop can capture a genuine, validly-signed `(raw_body, hmac)` pair emitted by Shopify for their own shop, and then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header rewritten to point at a victim shop. `HmacValidator.validate` will still pass because it only checks the (unmodified) body against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the event came from the victim shop.

### Impact Explanation
Any host application that uses `request.shop` from `Registry.process`'s callback to look up the merchant's session, scope a database write, or trigger merchant-specific business logic will process an attacker-fabricated event under the identity of a different tenant. That is a cross-tenant integrity issue: the attacker cannot read the victim's data through this vector, but they can inject events attributed to a shop they do not control (e.g., forged `orders/create`, `app/uninstalled`, or GDPR-topic payloads if the attacker also controls similarly-shaped webhook bodies from their own shop), degrading the tenant isolation guarantee this API contract implies.

### Likelihood Explanation
Exploitation requires the attacker to operate their own installation of the target app (freely available to anyone via the App Store/OAuth flow) in order to obtain a validly-signed body/HMAC pair, then send a crafted HTTP POST with swapped headers to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or victim credentials is required — only the ability to install the app once and control the header values presented to the endpoint, both of which are within reach of an unprivileged internet user.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is actually verified, e.g. include them in `to_signable_string`, or independently authenticate the shop by checking it against the caller's known/registered shop for the app installation before trusting `request.shop`, so a replayed body cannot be re-attributed to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint: headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of body B>`, body `B`.
3. Attacker replays the exact same body `B` and HMAC header to the endpoint but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches, so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, even though the body was never associated with the victim shop by Shopify.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
