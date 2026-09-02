### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but only the raw request body is included in the HMAC-signed material. `ShopifyAPI::Utils::HmacValidator.validate` therefore only proves that the *body* bytes were produced with the app's shared `api_secret_key` — it proves nothing about which shop (tenant) the request claims to be from. Any caller who can obtain one validly-signed webhook body/HMAC pair for their own shop can replay that exact body+HMAC while substituting an arbitrary `x-shopify-shop-domain` header, and `Registry.process` will accept it and dispatch it to the app's handler tagged with the attacker-chosen shop.

### Finding Description
The identity binding that should hold is:
`shop value trusted by the handler (request.shop) == shop value actually authenticated by the HMAC`

In `lib/shopify_api/webhooks/request.rb`: [1](#0-0) 

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`to_signable_string` (the data that gets HMAC-verified) is only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from attacker-controllable HTTP headers and are never mixed into the signed material.

`HmacValidator.validate` confirms this — it computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the body) using the app's `api_secret_key`, and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` then trusts `request.shop` and forwards it to the application's handler as the identity of the webhook's originating tenant: [4](#0-3) 

Because the `api_secret_key` is a single, shared secret for the whole app across all installing shops (not shop-specific), any unprivileged merchant who has installed the app can:
1. Trigger a real Shopify webhook for their own shop (a benign, legitimate action), capturing the genuine `raw_body` and the correctly computed `x-shopify-hmac-sha256` value that Shopify sent.
2. Replay that exact `raw_body` + HMAC to the app's webhook endpoint, but with the `x-shopify-shop-domain` header changed to a victim shop's domain.
3. `HmacValidator.validate` still succeeds because the signature only covers `raw_body`, which was untouched.
4. `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the forged victim domain, so the host application will act as though the event originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for the host application: an unprivileged user of one tenant can make the app process authenticated-looking webhook data as if it belongs to a different tenant, i.e., cross-tenant access/spoofing, without needing the victim's credentials, access token, or `client_secret`. Any downstream logic that trusts `request.shop`/`WebhookMetadata#shop` to look up sessions, access tokens or make authorization decisions can be manipulated into acting on/against a shop the attacker doesn't control.

### Likelihood Explanation
Any merchant who has installed the app (a normal, unprivileged position) can generate at least one legitimately signed webhook payload for their own shop by simply performing the action the webhook subscribes to (e.g., updating an order). Replaying that captured body/HMAC pair with a modified `shop-domain` header requires no secrets and is trivial to script, making this readily exploitable by any app-installing merchant.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the HMAC-signed material, or independently verify that the `shop-domain` header corresponds to a shop actually entitled to send the accompanying body/signature (e.g., derive/confirm shop identity from data embedded in the signed payload rather than an unauthenticated header). At minimum, document/enforce that consumers must cross-check `request.shop` against a shop known to be associated with the specific resource in the (signed) body before trusting it for tenant-sensitive operations.

### Proof of Concept
1. App installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing the same `api_secret_key`.
2. Attacker performs an action on their own shop that triggers a subscribed webhook topic (e.g. `orders/create`), and captures the resulting HTTP request Shopify sends: `raw_body` and the `x-shopify-hmac-sha256` header.
3. Attacker replays this request to the app's webhook endpoint unchanged except for the `x-shopify-shop-domain` header, setting it to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object where `hmac` and `to_signable_string` are unaffected by the header change.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checked `raw_body` against the secret [5](#0-4) .
6. `ShopifyAPI::Webhooks::Registry.process(request)` dispatches to the handler with `WebhookMetadata.new(... shop: request.shop ...)` set to `"victim-shop.myshopify.com"` [6](#0-5) , even though the event never happened on the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
