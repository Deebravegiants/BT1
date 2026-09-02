This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` and `topic` are read directly from unauthenticated headers [2](#0-1) . The docs explicitly tell integrators that `data.shop` is "The shop domain of the webhook" and safe to use for dispatching work per-tenant [3](#0-2) , and `Registry.process` only validates the HMAC before handing the attacker-controllable `request.shop` straight to the handler as tenant identity [4](#0-3) .

### Title
Webhook `shop-domain` Header Not Bound to HMAC Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw JSON body against the app's `client_secret` via HMAC; the `shopify-shop-domain` (and `shopify-topic`) headers are never covered by that signature, yet they are passed unmodified into the handler as the authoritative tenant identity (`WebhookMetadata#shop`).

### Finding Description
The identity binding that should hold is:
`shop bound inside the HMAC-signed payload == shop attributed to the webhook by the handler`

In `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are never part of the signed material: [5](#0-4) 

`Registry.process` validates the HMAC of the whole `Request` object (which, per `VerifiableQuery`, only checks `to_signable_string`, i.e., the body) and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

`HmacValidator.validate` only computes/compares the HMAC over `verifiable_query.to_signable_string`, never over the `shop` or `topic` fields: [6](#0-5) 

Before/after the attack:
- **Before**: legitimate webhook for Shop A → body B, `shop-domain: A.myshopify.com`, `hmac = HMAC(secret, B)`. HMAC is valid, `data.shop == "A"`.
- **After attacker's request sequence**: same secret is shared by the app across all its installed shops. An attacker who owns/operates Shop A (or otherwise obtains one legitimate `(body, hmac)` pair, e.g., by installing the app themselves) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting `shopify-shop-domain: B.myshopify.com` for a victim Shop B. `HmacValidator.validate` still returns `true` (it never inspected `shop`), so `Registry.process` dispatches to the handler with `WebhookMetadata#shop == "B"`, i.e., data that actually originated from Shop A is now attributed to Shop B.

This breaks the "shop authenticated vs. shop used as identity/session key" binding described in scope: the value verified by the HMAC (the body bytes only) is not the same value used to select/attribute the tenant (the header-derived `shop`).

### Impact Explanation
Because host applications are documented to trust `data.shop` as the authenticated tenant for dispatching background jobs, updating per-shop records, or handling sensitive lifecycle topics (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`), an attacker who controls one legitimate webhook body/HMAC pair for their own shop can cause the app to process and attribute that payload to an arbitrary victim shop domain. This is a cross-tenant data/action confusion — the exact "Critical: cross-tenant access" class in scope, since the gem's own `Registry.process`/`Request` design allows the tenant-identifying field to be forged independently of the cryptographic check that is supposed to authenticate the message.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be able to reach the app's webhook HTTP endpoint (unprivileged internet access, as the app's webhook route is public), and (2) the attacker possess one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` — trivially obtainable by installing the target app on their own shop and capturing a real webhook delivery, or from a topic whose body is attacker-influenceable (e.g., a webhook fired from data the attacker themselves entered in their own shop). No access token, `client_secret`, or privileged account is required to perform the forgery step itself.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`, `webhook-id`) in the HMAC-signed material used by `to_signable_string`, or otherwise cryptographically bind `shop` to the payload before it is trusted as tenant identity in `WebhookMetadata`. At minimum, document and/or enforce that `data.shop` must be cross-checked by the host application against a known/installed shop list before being used as a tenant key, since the current signature does not protect it.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and receives
# a legitimate webhook with a real HMAC computed over body B by Shopify using the
# app's shared client_secret.
real_body = '{"id": 1, "email": "victim-data@example.com"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, real_body)

# Attacker replays the identical body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim shop they do not control.
forged_headers = {
  "shopify-topic" => "customers/data_request", # or any registered topic
  "shopify-hmac-sha256" => Base64.encode64(real_hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, not authenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: real_body, headers: forged_headers)

# HmacValidator only checks `real_body`, so this succeeds even though shop-domain was forged:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))
```
The handler receives `data.shop == "victim-shop.myshopify.com"` despite the payload never having originated from that shop, demonstrating the missing identity binding between the HMAC-verified bytes and the trusted tenant field.

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
