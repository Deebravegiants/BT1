### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook confusion - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `HMAC(secret, raw_body)` matches the `hmac-sha256` header, then hands the app a `WebhookMetadata` object built from `request.shop` — a value taken straight from the unauthenticated `shop-domain` header, never part of the signed data. Any tenant of a multi-tenant app can capture one of its own genuine webhook deliveries and replay the identical body/HMAC pair while spoofing the `shop-domain` header to name a different (victim) shop, and `Registry.process` will accept it as valid and attribute the payload to the victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shop-domain` header with no cryptographic binding at all: [2](#0-1) 

`Registry.process` performs exactly one check — HMAC over the body — and then constructs `WebhookMetadata` using this unauthenticated `request.shop`, handing it to the app's handler as the trusted tenant identifier for the payload: [3](#0-2) 

The intended binding this mechanism is supposed to provide is:
`HMAC(secret, raw_body) valid  ⟺  (raw_body, shop) originated together from Shopify for that specific shop`

What is actually enforced is only:
`HMAC(secret, raw_body) valid  ⟺  raw_body was produced by Shopify for *some* shop using this app's shared secret`

Because the same `client_secret`/app secret is shared across every shop that installs the app, any shop's valid `(raw_body, hmac)` pair remains valid HMAC-wise no matter what `shop-domain` header accompanies it. The `shop` field that the rest of the pipeline treats as authenticated (it is exposed via `WebhookMetadata#shop` specifically so host apps can select which tenant's session/data the payload belongs to) is never included in `to_signable_string` and is therefore fully attacker-controllable independent of the signature check.

### Impact Explanation
This breaks the tenant-identity binding the HMAC check is presumed to provide. Any merchant that installs the app (an "unprivileged" actor relative to other tenants of the same app) can:
1. Receive a legitimate webhook for their own shop A — capturing `raw_body` and the valid `x-shopify-hmac-sha256` value.
2. Replay the exact same `raw_body`/HMAC pair to the app's webhook endpoint, but with `x-shopify-shop-domain` (or `shopify-shop-domain`) rewritten to shop B's domain.
3. `Registry.process` validates HMAC successfully (body unchanged) and calls the handler with `WebhookMetadata.new(shop: "B", body: <shop A's data>, ...)`.

Any host application that follows the gem's documented pattern of using `WebhookMetadata#shop` to look up the corresponding session/access token and act on the enclosed `body` for that shop will now process/store tenant-A data under tenant B's identity (or vice versa) despite a "successfully verified" webhook. This is a cross-tenant data confusion vulnerability — Critical impact per the given classification (cross-tenant access), since it lets one tenant inject falsified/misattributed data into another tenant's context without ever needing the app's `client_secret` or any privileged credential.

### Likelihood Explanation
Likelihood is High-to-Medium: the attacker only needs to be a merchant who has legitimately installed the target app (a low bar, no special privilege, no leaked secrets required) and the ability to intercept/replay their own webhook HTTP requests to the app's public webhook endpoint (trivial with any HTTP client). No knowledge of `api_secret_key` or any other tenant's credentials is required — only the ability to observe traffic to their own endpoint, which is fully within an unprivileged user's control.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signable string used for HMAC verification, or otherwise cryptographically bind the claimed shop to the payload before exposing `WebhookMetadata#shop` to handlers. At minimum, document prominently (and enforce in-library where possible) that `WebhookMetadata#shop` must be independently cross-checked against the shop associated with the specific `webhook_id`/subscription registered via `Registry.register`, rather than trusted as an authenticated identity derived from HMAC validation.

### Proof of Concept
```ruby
# Attacker is a legitimate merchant of shop-a.myshopify.com using the same target app.
# Step 1: capture a real webhook delivery to the app's endpoint.
raw_body = '{"id":123,"note":"legit order data for shop-a"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Step 2: replay identical body/HMAC but spoof the shop-domain header to victim shop-b.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),   # still valid! body unchanged
  "x-shopify-shop-domain" => "shop-b.myshopify.com",  # forged victim shop
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Step 3: Registry.process accepts it — HMAC check only covers raw_body, not shop.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler invoked with WebhookMetadata(shop: "shop-b.myshopify.com", body: <shop-a's data>)
```
`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) will not raise `InvalidWebhookError` because `HmacValidator.validate` only checks `raw_body`, confirming the identity-binding gap.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
