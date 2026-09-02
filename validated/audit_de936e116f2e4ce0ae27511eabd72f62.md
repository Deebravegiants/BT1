## Analysis Result [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC of the raw request body. The `shop` (tenant) identity that is subsequently handed to the app's webhook handler is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. This breaks the identity binding `hmac(body) == valid ⟹ shop-domain-header is trustworthy`. An attacker who legitimately installs the app on their own store (and therefore possesses body+HMAC pairs that are valid under the app's shared `api_secret_key`) can replay that exact payload while substituting an arbitrary `shop-domain` header value, and the gem will treat the replayed data as if it originated from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`:
```ruby
def to_signable_string
  @raw_body
end
```
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., the body) and compares it to the `hmac` header:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
```
`ShopifyAPI::Webhooks::Registry.process` performs this check and, if it passes, immediately trusts `request.shop` — sourced from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header — to build the `WebhookMetadata` passed to the app's handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
end
```
Because `api_secret_key` is a single value shared by the app across all installing shops (not per-shop), any body+HMAC pair that is valid for shop A is also a valid signature for the identical body when replayed with a different `shop` header. The signature check has no way to detect that the tenant label has changed, since `shop`, `topic`, `webhook_id`, and `api_version` are never part of the signed bytes.

### Impact Explanation
This breaks the tenant isolation ("cross-tenant access") relied upon by multi-tenant Shopify apps: an attacker with a normal, legitimate install of the app on their own store can forge webhook events that the app attributes to any other shop by simply changing one HTTP header while replaying a previously captured, validly-signed body. Depending on how the host application's webhook handlers use `data.shop` (e.g., `app/uninstalled` triggering deprovisioning, `orders/create`/`customers/*` writing tenant-scoped records, GDPR mandatory webhooks), this can be used to inject or corrupt data under an arbitrary victim shop's tenant, or trigger administrative actions (like uninstall cleanup) against a shop the attacker doesn't control — a cross-tenant impact.

### Likelihood Explanation
The prerequisite is that the attacker holds one valid (body, hmac) pair, which they can trivially obtain by installing the app on their own store and observing any webhook delivery. No access to `api_secret_key`, access tokens, or any victim credential is required. The victim's `shop` domain in a typical replay is also easily guessable (`{shop-name}.myshopify.com`). This is a low-effort, unprivileged-attacker path.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, or otherwise validate that the shop asserted in the header corresponds to a shop known to have this specific `webhook_id`/subscription (e.g., cross-check against the app's own webhook registration/session store) before trusting it, rather than accepting any header value once the raw-body HMAC checks out.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and configures/observes a webhook delivery (e.g., `orders/create`), capturing the raw body and its `X-Shopify-Hmac-Sha256` value — both valid under the app's shared `api_secret_key`.
2. Attacker sends a POST request to the app's webhook endpoint with the identical captured body and `hmac` header, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `hmac == HMAC(secret, raw_body)` — this still passes because the body is unchanged.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker's data, ...)`, causing the host app to process attacker-controlled data as if it came from `victim-shop.myshopify.com`.

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
