### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are trusted from unauthenticated headers while only the raw body is HMAC-verified - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC signature to the raw request body only. The `shop`, `topic`, `api_version`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` hands to the app's webhook handler as the tenant/routing identity are read straight from HTTP headers that are never covered by that signature.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are read from headers and are not part of `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and constant-time compares it to the received signature — i.e. it authenticates only the body bytes, never the header values: [3](#0-2) 

`Registry.process` then does:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

The identity equality that should hold is:

`shop_that_produced_a_valid_signature == shop_passed_to_the_handler`

but the actual check only proves:

`HMAC(api_secret_key, raw_body) == received_hmac`

with `request.shop` (and `topic`/`webhook_id`) sourced from `x-shopify-shop-domain`/`shopify-shop-domain` headers that participate in neither side of that comparison. Any request whose body/HMAC pair is valid for the app's `api_secret_key` will be accepted regardless of which `shop-domain`, `topic`, or `webhook-id` header accompanies it, because those headers are never mixed into the signed string.

### Impact Explanation
This is a cross-tenant identity-binding break of the kind called out for this scan (field acted on — `shop`/`topic`/`webhook_id` used to route and tag data for a specific tenant — but not covered by the HMAC that is supposed to authenticate the request). A multi-tenant app that dispatches on `WebhookMetadata#shop`/`#topic` (as the library's own test suite demonstrates it should: `assert_equal(@shop, data.shop)` in `test/webhooks/registry_test.rb`) can be made to process or persist attacker-supplied body content under an arbitrary victim shop identity, or under an arbitrary topic, as long as the attacker can produce (not forge) a body+HMAC pair that is valid for the app's own secret — e.g. by replaying a webhook the app itself received for its own installed shop but with the `shop-domain`/`topic`/`webhook-id` headers swapped to a different value. Because `HmacValidator.validate` never binds these header values into the signature, `Registry.process` cannot distinguish this from a genuine webhook for that shop/topic, resulting in cross-tenant data confusion in the handler layer.

### Likelihood Explanation
Any endpoint exposed to accept Shopify webhook POSTs is reachable by an unauthenticated internet client; no access token, `api_secret_key`, or privileged account is required to send the crafted request, and the vulnerable comparison (`to_signable_string` returning only `@raw_body`) is exercised on every call to `Registry.process`, which is the library's documented entry point for webhook handling.

### Recommendation
Bind the routing/identity headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the signed string, or otherwise require the caller to separately authenticate/attest the shop before trusting `request.shop`/`request.topic` for handler dispatch, so that the equality `hmac_verified_identity == identity_delivered_to_handler` actually holds.

### Proof of Concept
1. App has an installed shop `victim-shop.myshopify.com` and its own shop `attacker-shop.myshopify.com` (attacker is a legitimate merchant/tenant of the multi-tenant app).
2. Shopify sends the attacker's own shop a legitimate webhook: body `B`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`, and a valid `x-shopify-hmac-sha256` computed over `B` with the app's `api_secret_key`.
3. Attacker replays the exact same request to the app's webhook endpoint but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com` (and/or `x-shopify-topic`), keeping body `B` and the HMAC header unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses the new headers; `Utils::HmacValidator.validate` still succeeds because `to_signable_string` is just `@raw_body` (`B`), which is unchanged.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: <attacker-chosen>, body: parsed(B), ...)`, causing the app to act on/persist attacker-controlled data tagged as belonging to `victim-shop.myshopify.com`.

### Citations

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
