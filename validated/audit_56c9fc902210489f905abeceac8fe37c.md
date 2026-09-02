### Title
Webhook Shop Attribution Not Covered by HMAC Signature Enables Cross-Tenant Webhook Forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the shop that a webhook is attributed to comes from the unsigned `x-shopify-shop-domain` header. Because every shop installed on an app shares the same `api_secret_key`, any shop that receives a legitimate webhook from the app can replay that exact body/HMAC pair while swapping the `shop-domain` header to a victim shop, and `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and hand the attacker-chosen shop to the app's handler.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and secure-compares it to the received HMAC: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body — it excludes the `shop`, `topic`, and `webhook_id` header values entirely: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` (parsed straight from the unauthenticated `shopify-shop-domain` header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop authenticated by HMAC == shop attributed to the webhook payload`. Here the HMAC only authenticates `(api_secret_key, raw_body)`; it says nothing about which shop the payload belongs to. Since `api_secret_key` is a single value shared by the app across **all** installed shops, the same `(body, hmac)` pair is valid for every shop. An attacker who controls or observes a webhook delivery for their own shop (or any shop, since webhook payloads for the same topic/body content are often generic/predictable, e.g. `app/uninstalled` bodies, or simply captured from their own store) can resend that exact body and HMAC with a forged `x-shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` still succeeds because it never looks at the shop header, and `Registry.process` will call the app's handler with `shop: <victim-shop>`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee to host applications: a webhook that "verified successfully" is not proven to originate from the shop it claims. Any app that relies on `WebhookMetadata#shop` (as documented/intended by this gem) to select which merchant's data/session to act on can be made to process a forged webhook under a different tenant's identity — e.g. an `app/uninstalled` or `shop/redact` webhook forged for a victim shop, causing the app to delete/alter the victim's data, or a data-carrying webhook forged to inject attacker data attributed to the victim shop. This is a cross-tenant access vulnerability achieved purely through the gem's own HMAC-based trust mechanism.

### Likelihood Explanation
Any merchant that installs the target app (an "unprivileged internet user" relative to other tenants) can trivially capture a legitimate webhook body and its valid HMAC for their own shop by running the app in their own store — no `api_secret_key` or access token theft is required, since the attacker never needs to compute a new signature, only replay the one they legitimately received. Forging the `x-shopify-shop-domain` header is a standard, unauthenticated HTTP header they control when replaying the request to the app's webhook endpoint.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) inside the HMAC-covered material, or independently verify that the shop asserted in the header matches a shop expected/known for that specific delivery (e.g., cross-check against the webhook subscription's registered shop, or require the shop to also be echoed and bound inside the signed payload). At minimum, `to_signable_string` should incorporate the `shop-domain` header so that a captured `(body, hmac)` pair for shop A cannot be replayed while claiming to be shop B.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers/receives a legitimate webhook, e.g. `orders/create`, capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed by Shopify using the app's shared `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Utils::HmacValidator.validate` recomputes HMAC over `to_signable_string` (`= B` only) and it matches `H`, so validation passes.
4. `ShopifyAPI::Webhooks::Registry.process` calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to act on victim-shop's tenant context using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
