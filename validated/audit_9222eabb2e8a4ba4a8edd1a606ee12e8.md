### Title
Webhook HMAC signature does not cover the `topic` or `shop-domain` headers, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `Registry.process` trusts the unauthenticated `topic` and `shop` header values to decide which handler to invoke and which tenant the event belongs to. The identity binding that should hold is:

`bytes_covered_by_hmac == bytes_the_registry_acts_on`

but here `bytes_covered_by_hmac == raw_body` while `bytes_the_registry_acts_on == {raw_body, topic_header, shop_header}`. This is the exact class of bug described in the report ("a field acted on but not covered by the HMAC"), analogous to code trusting a value that was never cryptographically checked.

### Finding Description
`HmacValidator.validate` computes and compares the signature only against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only the raw body, excluding the `topic`, `shop`, `api_version`, and `webhook_id` headers: [2](#0-1) 

`Registry.process` validates the HMAC, then unconditionally trusts `request.topic` to select the handler and `request.shop` to identify the tenant, passing both to the handler without any further binding to the signed content: [3](#0-2) 

Because `topic` and `shop-domain` are plain HTTP headers that are never mixed into the HMAC input, any request whose **body** carries a valid signature (computed by Shopify's servers with the real `api_secret_key` for some legitimate webhook delivery) can be replayed with an **arbitrary** `topic` and `shop-domain` header, and the signature check will still pass. This breaks the binding `shop/topic authenticated by Shopify == shop/topic acted upon by the handler`.

### Impact Explanation
An unprivileged actor who legitimately installs the app on their own (e.g. free dev) store will receive genuine webhook deliveries signed with the real secret over some JSON body. That actor can:
1. Capture one such delivery (any topic, e.g. `carts/update`).
2. Resend the same raw body and HMAC to the app's public webhook endpoint, but replace the `x-shopify-topic` header with a sensitive topic such as `app/uninstalled`, and the `x-shopify-shop-domain` header with any victim shop domain.
3. `Utils::HmacValidator.validate` still succeeds (it only checks the body), `Registry.process` selects the handler registered for `app/uninstalled`, and calls it with `shop: "victim-shop.myshopify.com"`.

Depending on what the app's handler does for that topic (commonly: revoking/deleting stored sessions and access tokens for the shop), this gives cross-tenant control over another merchant's app data/session state — a Critical, cross-tenant impact — without possessing the victim's credentials, access token, or `client_secret`.

### Likelihood Explanation
Any user can install the target app on a store they control and thereby obtain at least one validly-signed webhook body/HMAC pair — no leaked secrets or privileged access required. Forging the `topic`/`shop-domain` headers on the replayed HTTP request requires no special capability, since the gem itself never binds those headers into the signed payload. Likelihood is high for any app relying solely on `ShopifyAPI::Webhooks::Registry.process` for authorization.

### Recommendation
Include the `topic`, `shop-domain`, `webhook_id`, and `api_version` values in the signable content (or otherwise cryptographically/contextually bind them, e.g. verify `request.shop` matches an actual installed/active session before dispatching, and verify `request.topic` matches the topic the handler was registered for against an out-of-band source of truth), so that HMAC validation covers everything the registry subsequently acts upon.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a genuine webhook delivery, e.g. `carts/update`, with headers `x-shopify-hmac-sha256: <validHmac>` computed over body `B`.
2. Send an HTTP request to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256` header, but set:
   - `x-shopify-topic: app/uninstalled`
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against the HMAC.
4. `Registry.process` looks up the handler for `app/uninstalled` and invokes it with `shop: "victim-shop.myshopify.com"`, causing the app to perform uninstall-cleanup logic against a shop the attacker does not own. [4](#0-3)

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
