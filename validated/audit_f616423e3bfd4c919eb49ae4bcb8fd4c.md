### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` fields are trusted despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, yet `ShopifyAPI::Webhooks::Registry.process` uses unauthenticated header values (`shop`, `topic`, `webhook_id`, `api_version`) to route and construct the data handed to the app's webhook handler. This breaks the identity binding the HMAC is supposed to guarantee: `hmac_valid == true` should imply `(shop, topic, body)` all originated together from Shopify, but only `body` is actually bound to the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body) and then dispatches using the untrusted `request.topic` and passes the untrusted `request.shop` straight into the data given to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms this: it signs/compares only `verifiable_query.to_signable_string`, which for webhooks is the raw body: [4](#0-3) 

Because the webhook HMAC secret (`Context.api_secret_key`) is the app's single client secret — shared across every shop that has installed the app, not a per-shop value — any shop that has legitimately installed the app can capture a real, validly-signed webhook delivery it receives from Shopify (e.g. a webhook with an empty or attacker-influenced body) and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id` and `X-Shopify-Api-Version` headers rewritten to any values of the attacker's choosing. `Utils::HmacValidator.validate` still returns `true` because it only re-derives the HMAC from the body, so `Registry.process` accepts the forged request and calls the registered handler with `WebhookMetadata.new(topic: <attacker-controlled>, shop: <attacker-controlled>, body: ..., webhook_id: <attacker-controlled>, api_version: <attacker-controlled>)`.

This is the same class of bug as the external report: a boolean/flag ("HMAC valid") is treated as proof of an identity binding ("this event genuinely belongs to shop X, topic Y") that the signature never actually covered.

### Impact Explanation
An unprivileged internet user who can install the target app on any shop (including a shop of their own creation) gains the ability to forge webhook events attributed to an arbitrary victim shop and arbitrary topic — including the mandatory GDPR topics `customers/redact`, `shop/redact`, and `customers/data_request` — while passing HMAC validation. Any host application that trusts `WebhookMetadata#shop`/`#topic` (as the gem's own documentation and design intends) to key its per-tenant logic (e.g., looking up/deleting a shop's data, updating billing state, revoking access, triggering redaction) can be made to act on behalf of, or against, a shop the attacker does not control — a cross-tenant confusion crossing a real tenant boundary, consistent with the "Critical – cross-tenant access" impact bucket.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on any shop (a normal, unprivileged action any developer/merchant can perform for a public or development app), (2) capturing one legitimately delivered webhook (trivial, since apps must expose a reachable webhook endpoint), and (3) replaying it with modified headers to the same endpoint. No access to `api_secret_key`, tokens, or the victim's environment is needed.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content used for HMAC verification, or otherwise cryptographically bind them to the signed body (e.g., verify them against Shopify's canonical webhook payload/topic rather than trusting the raw header values). At minimum, document and enforce that `Registry.process`/`WebhookMetadata` must not be treated as proof of shop/topic authenticity beyond body integrity, and provide a built-in check that the `shop` header corresponds to a shop session/installation known to the app before dispatching to handlers.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; receive a legitimate webhook delivery, e.g. body `{}` with headers:
   ```
   X-Shopify-Topic: app/uninstalled
   X-Shopify-Hmac-Sha256: <valid HMAC of "{}">
   X-Shopify-Shop-Domain: attacker.myshopify.com
   ```
2. Replay the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but with headers rewritten:
   ```
   X-Shopify-Topic: customers/redact
   X-Shopify-Hmac-Sha256: <same valid HMAC of "{}">
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)` is constructed, `Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`) because only the body is checked.
4. `Registry.process` dispatches to the `customers/redact` handler with `shop: "victim-shop.myshopify.com"` (per `lib/shopify_api/webhooks/registry.rb:188-199`), causing the host app to act on the victim shop's data despite the request never originating from Shopify for that shop/topic.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
