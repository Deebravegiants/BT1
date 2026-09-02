## Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using a `shop` value taken from an unauthenticated header. Because the shop identifier is never part of the signed material, a valid `(body, hmac)` pair captured from one tenant's legitimate webhook delivery can be replayed with a different `x-shopify-shop-domain` header to make the gem attribute the webhook to an arbitrary victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` and compares it to the received HMAC — it never incorporates `shop`, `topic`, or `webhook_id`: [2](#0-1) 

`Registry.process` uses this same, body-only HMAC check as its sole authentication gate, then builds `WebhookMetadata` for the handler using `request.shop`, which is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that was never covered by the signature: [3](#0-2) [4](#0-3) 

The equality the design relies on is:
`shop_used_for_tenant_dispatch == shop_covered_by_hmac`

but in fact `shop_covered_by_hmac` is undefined — only the body bytes are authenticated — so this equality never holds. An attacker who controls a legitimate, unprivileged installation of the app on their own store (Shop A) can:
1. Trigger a webhook delivery to their own app endpoint (e.g. `app/uninstalled`, or any topic the host app registers a handler for) and capture the genuine `raw_body` and its valid `x-shopify-hmac-sha256` value — both computed by Shopify itself using the app's real secret, so no secret leakage or guessing is required.
2. Resend that exact `(raw_body, hmac)` pair to the same webhook endpoint, substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`) to name a victim store, Shop B.
3. `HmacValidator.validate` still succeeds because it re-derives the same signature from the same `raw_body`; `Registry.process` then invokes the registered handler with `WebhookMetadata.shop == "shop-b.myshopify.com"`.

Any host application logic that trusts `data.shop` to look up/mutate per-tenant state (e.g., revoking or updating a stored session/access token on `app/uninstalled`, updating per-shop settings on `shop/update`, etc.) will act on Shop B's tenant record using data supplied entirely by the Shop A attacker — a cross-tenant identity confusion introduced by the gem's HMAC scope not matching the field it uses for tenant dispatch.

### Impact Explanation
This crosses a tenant boundary: an unprivileged attacker who legitimately controls only their own shop's app installation can forge webhook events attributed to a different merchant's shop, without needing that merchant's access token, the app's `client_secret`, or any privileged access. Depending on the host's webhook handler (a very common pattern being session/token invalidation or state changes keyed off `data.shop` for mandatory topics like `app/uninstalled`), this can be leveraged to disrupt or manipulate another tenant's stored session state — a cross-tenant access/integrity issue.

### Likelihood Explanation
High. The only precondition is that the attacker has (or creates) their own store with the target app installed — a fully unprivileged, self-service action — and that the app registers at least one webhook handler that reads `data.shop`, which is the documented and expected usage pattern of `WebhookMetadata` in this gem.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed/verified material before it is trusted for dispatch, or independently cross-check the header-derived `shop` against a value the app already has authenticated for that specific delivery (e.g., verify the shop is one for which a session/install record already exists) before acting on webhook data. At minimum, document that `WebhookMetadata#shop` is not cryptographically bound to the HMAC and must not be used as the sole tenant key for state-changing operations.

### Proof of Concept
```ruby
raw_body = '{"id":123}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Step 1: attacker's own shop legitimately triggers this webhook and the attacker
# captures the (raw_body, hmac) pair Shopify sent for "shop-a.myshopify.com".

# Step 2: attacker replays it, spoofing a different shop-domain header:
forged_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by the HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation succeeds; handler is invoked with data.shop == "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
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
